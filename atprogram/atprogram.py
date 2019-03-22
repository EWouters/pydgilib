from os import path, getenv, getcwd
from subprocess import run, PIPE, STDOUT

import re


def atprogram(project_path=None, device_name="ATSAML11E16A", verbose=0,
              clean=False, build=True, erase=True, program=True, verify=False,
              tool="EDBG", interface="SWD", atmel_studio_path=path.join(
                  getenv("programfiles(x86)"), "Atmel", "Studio", "7.0"),
              make_path=None, atprogram_path=None, configuration="Debug",
              device_sn=None, jobs=getenv("NUMBER_OF_PROCESSORS"),
              make_command=None, atprogram_command=None, return_output=False,
              dry_run=False):
    """Atprogram.

    This function can compile projects and write them to a device. It
    determines what to do based on the arguments it gets. Specify at least one
    of `project_path`, `make_command` or `atprogram_command`.

    NOTE: Verification is known to return 23, also in command line.

    Keyword Arguments:
        project_path {str} -- Location where the project resides. If it ends in
            `.elf` the elf file will be used. If it ends in `Makefile` the
            Makefile will be used. Otherwise it should be a path to a folder
            which holds the `Debug` folder. (default: {None})
        device_name {str} -- Device name. E.g. atxmega128a1 or at32uc3a0256.
            (default: {"ATSAML11E16A"})
        verbose {int} -- Verbosity:
            - 0: Silent (default: {0})
            - 1: Info
            - 2: Debug
            - 3: List Commands
        clean {bool} -- Run make clean if True (default: {False})
        build {bool} -- Run make all if True (default: {True})
        erase {bool} -- Run atprogram chiperase if True (default: {True})
        program {bool} -- Run atprogram program if True (default: {True})
        verify {bool} -- Run atprogram verify if True (default: {False})
        tool {str} -- Tool name: avrdragon, avrispmk2, avrone, jtagice3,
            jtagicemkii, qt600, stk500, stk600, samice, edbg, medbg, nedbg,
            atmelice, pickit4, powerdebugger, megadfu or flip. (default:
            {"EDBG"})
        interface {str} -- Physical interface: aWire, debugWIRE, HVPP, HVSP,
            ISP, JTAG, PDI, UPDI, TPI or SWD. (default: {"SWD"})
        atmel_studio_path {[type]} -- Location where Atmel Studio is installed,
            ending in the folder named after the version, e.g. 7.0. (default:
            {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0")})
        make_path {[type]} -- Location where `make.exe` is installed. (default:
            {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0", "shellutils", "make.exe")})
        atprogram_path {[type]} -- Location where `atprogram.exe` is installed
            (default: {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0", "atbackend", "atprogram.exe")})
        configuration {str} -- Which configuration to use. (default: {"Debug"})
        device_sn {str} -- The programmer/debugger serialnumber. Must be
            specified when more than one debugger is connected. (default:
            {None})
        jobs {int} -- How many jobs *make* should use(default:
            {getenv("NUMBER_OF_PROCESSORS")})
        make_command {str} -- Options to pass to make `[options] [target] ...`
            (default: {None})
        atprogram_command {str} -- Command(s) to pass to atprogram: `[options]
            <command> [arguments] [<command> [arguments] ...]` (default:
            {None})
        return_output {bool} -- If True the return value will be the output,
            else it will be the return code (default: {False})
        dry_run {bool} -- Whether to run the commands using the subprocess
            module or just print the commands (default: {False})

    Raises:
        ValueError -- Need to specify at least one of `project_path`,
            `make_command` or `atprogram_command`.

    Returns:
        int -- A non-zero return value indicates the subprocess call returned
            an error.

    """
    elf_mode = False
    makefile_mode = False
    makefile_path = None
    if project_path is not None:
        elf_mode = path.splitext(project_path)[1] is ".elf"
        makefile_path, makefile = path.split(project_path)
        makefile_mode = makefile is "Makefile"
        if not makefile_mode:
            makefile_path = path.join(project_path, configuration)
    elif make_command is None and atprogram_command is None:
        raise ValueError(
            "Need to specify at least one of project_path, make_command or " +
            "atprogram_command.")
    else:
        # This is make_command mode or atprogram_command mode
        clean = build = erase = program = verify = False
    output = SavePrint(return_output)
    stdout = PIPE if verbose >= 0 else None
    stderr = STDOUT if verbose >= 1 else None
    returncode = 0
    if not elf_mode and (clean or build or make_command):
        make_path = make_path or path.join(
            atmel_studio_path, "shellutils", "make.exe")

        def make_caller(command):
            args = ([make_path] + command.split())
            kwargs = dict(cwd=makefile_path, stdout=stdout, stderr=stderr)
            if dry_run:
                output.print("".join(kwargs.get("cwd", getcwd())
                                     ) + "> " + " ".join(args))
                return 0
            res = run(args, **kwargs)
            if verbose:
                output.print(res.stdout.decode())
            return res.returncode
        if make_command and not returncode:
            returncode = make_caller(make_command)
        if clean and not returncode:
            returncode = make_caller("clean")
        if build and not returncode:
            returncode = make_caller(f"all --jobs {jobs} --output-sync")
    if (not makefile_mode and
            (erase or program or verify or atprogram_command) and
            not returncode):
        atprogram_path = atprogram_path or path.join(
            atmel_studio_path, "atbackend", "atprogram.exe")

        def atprogram_caller(command):
            args = ([atprogram_path] + (verbose-1) * ["-v"] + command.split())
            kwargs = dict(stdout=stdout, stderr=stderr)
            if dry_run:
                output.print(getcwd() + "> " + " ".join(args))
                return 0
            res = run(args, **kwargs)
            if verbose:
                output.print(res.stdout.decode())
            return res.returncode
        elf_file_path = None if not (program or verify) else project_path if \
            elf_mode else path.join(project_path, configuration,
                                    path.basename(project_path)) + ".elf"
        atprogram_command = \
            f"-t {tool} -i {interface} -d {device_name} " + \
            (device_sn is not None) * f" -s {device_sn} " + \
            (atprogram_command or
             erase * " chiperase " +
             program * f" program -f {elf_file_path} " +
             verify * f" verify -fl -f {elf_file_path} " +
             (verbose >= 3) * " info")
        returncode = atprogram_caller(atprogram_command)
        if returncode:
            atprogram_caller("exitcode")
    if return_output:
        return output.output + f"\n{returncode}"
    else:
        return returncode


class SavePrint(object):
    def __init__(self, return_output):
        self.return_output = return_output
        self.output = ""

    def print(self, s):
        if self.return_output:
            self.output += s
        else:
            print(s)


def get_device_info(
        device_name="ATSAML11E16A", verbose=0, tool="EDBG", interface="SWD",
        atmel_studio_path=path.join(
            getenv("programfiles(x86)"), "Atmel", "Studio", "7.0"),
        atprogram_path=None, device_sn=None):
    """get_device_info.

    [description]

    Keyword Arguments:
        device_name {str} -- Device name. E.g. atxmega128a1 or at32uc3a0256.
            (default: {"ATSAML11E16A"})
        verbose {int} -- Print results (default: {0})
        tool {str} -- Tool name: avrdragon, avrispmk2, avrone, jtagice3,
            jtagicemkii, qt600, stk500, stk600, samice, edbg, medbg, nedbg,
            atmelice, pickit4, powerdebugger, megadfu or flip. (default:
            {"EDBG"})
        interface {str} -- Physical interface: aWire, debugWIRE, HVPP, HVSP,
            ISP, JTAG, PDI, UPDI, TPI or SWD. (default: {"SWD"})
        atmel_studio_path {[type]} -- Location where Atmel Studio is installed,
            ending in the folder named after the version, e.g. 7.0. (default:
            {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0")})
        atprogram_path {[type]} -- Location where `atprogram.exe` is installed
            (default: {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0", "atbackend", "atprogram.exe")})
        device_sn {str} -- The programmer/debugger serialnumber. Must be
            specified when more than one debugger is connected. (default:
            {None})
    """
    atprogram_info = atprogram(
        atprogram_command="info", return_output=True, verbose=1,
        device_name=device_name, tool=tool, interface=interface,
        atmel_studio_path=atmel_studio_path, atprogram_path=atprogram_path,
        device_sn=device_sn, dry_run=False)
    device_info = {
        "Target voltage": float(re.findall(
            r"\nTarget voltage:\s(\d+(\.\d+)?)\sV", atprogram_info)[0][0]),
        "Device information": {
            "Name": re.findall(r"\nName:\s+(\S+)\s+", atprogram_info)[0],
            "JtagId": re.findall(r"\nJtagId:\s+(\S+)\s+", atprogram_info)[0],
            "CPU arch.": re.findall(r"\nCPU arch.:\s+(\S+)\s+", atprogram_info)[0],
            "Series": re.findall(r"\nSeries:\s+(\S+)\s+", atprogram_info)[0],
            "DAL": int(re.findall(r"\nDAL:\s+(\d+)\s+", atprogram_info)[0])},
        "Memory Information": {
            "base": {
                address_space: [int(start_address, 16), int(size, 16)]
                for address_space, start_address, size in re.findall(
                    r"\n  (\w+)\s+(0[xX][0-9a-fA-F]+)\s+(0[xX][0-9a-fA-F]+)\s+\n",
                    atprogram_info)},
            "fuses": {
                fuse: int(value, 16) for fuse, value in re.findall(
                    r"\n   (\w+)\s+(0[xX][0-9a-fA-F]+)\s+\n", atprogram_info)}
        }
    }
    if verbose >= 2:
        print(device_info)
    return(device_info)


size_regexp = re.compile(
    r"\.elf\"\n\s*text\t\s*data\t\s*bss\t\s*dec\t\s*hex\t\s*filename\r\n\s*" +
    r"(\d+)\t\s*(\d+)\t\s*(\d+)\t\s*(\d+)\t\s*([0-9a-fA-F]+)\t\s*(\S+.elf)")


def get_project_size(
        project_path, device_name="ATSAML11E16A", verbose=0, tool="EDBG",
        interface="SWD", atmel_studio_path=path.join(
            getenv("programfiles(x86)"), "Atmel", "Studio", "7.0"),
        make_path=None, configuration="Debug", device_sn=None,
        jobs=getenv("NUMBER_OF_PROCESSORS")):
    """get_project_size.

    Keyword Arguments:
        project_path {str} -- Location where the project resides. If it ends in
            `.elf` the elf file will be used. If it ends in `Makefile` the
            Makefile will be used. Otherwise it should be a path to a folder
            which holds the `Debug` folder.
        device_name {str} -- Device name. E.g. atxmega128a1 or at32uc3a0256.
            (default: {"ATSAML11E16A"})
        verbose {int} -- Print results (default: {0})
        tool {str} -- Tool name: avrdragon, avrispmk2, avrone, jtagice3,
            jtagicemkii, qt600, stk500, stk600, samice, edbg, medbg, nedbg,
            atmelice, pickit4, powerdebugger, megadfu or flip. (default:
            {"EDBG"})
        interface {str} -- Physical interface: aWire, debugWIRE, HVPP, HVSP,
            ISP, JTAG, PDI, UPDI, TPI or SWD. (default: {"SWD"})
        atmel_studio_path {[type]} -- Location where Atmel Studio is installed,
            ending in the folder named after the version, e.g. 7.0. (default:
            {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0")})
        make_path {[type]} -- Location where `make.exe` is installed. (default:
            {path.join(getenv("programfiles(x86)"), "Atmel", "Studio", "7.0", "shellutils", "make.exe")})
        configuration {str} -- Which configuration to use. (default: {"Debug"})
        device_sn {str} -- The programmer/debugger serialnumber. Must be
            specified when more than one debugger is connected. (default:
            {None})
        jobs {int} -- How many jobs *make* should use(default:
            {getenv("NUMBER_OF_PROCESSORS")})

    Returns:
        dict -- A dictionary of sizes of the sections, the total size and the
            file name.

    """
    (text, data, bss, dec, hex, filename) = size_regexp.findall(atprogram(
        project_path, clean=True, build=True, erase=False, program=False,
        verify=False, return_output=True, verbose=1, dry_run=False))[0]
    result = {"text": int(text), "data": int(data), "bss": int(
        bss), "dec": int(dec), "hex": int(hex, 16), "filename": filename}
    if verbose >= 2:
        print(result)
    return result
