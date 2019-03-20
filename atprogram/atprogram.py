from os import path, getenv, getcwd
from subprocess import run, PIPE, STDOUT


def atprogram(project_path=None, device_name="ATSAML11E16A", verbose=0,
              clean=False, build=True, erase=True, program=True, verify=False,
              tool="EDBG", interface="SWD", atmel_studio_path=path.join(
                  getenv("programfiles(x86)"), "Atmel", "Studio", "7.0"),
              make_path=None, atprogram_path=None, configuration="Debug",
              device_sn=None, jobs=getenv("NUMBER_OF_PROCESSORS"),
              make_command=None, atprogram_command=None, dry_run=False):
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
        dry_run {bool} -- [description] (default: {False})

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
    stdout = PIPE if verbose >= 0 else None
    stderr = STDOUT if verbose >= 1 else None
    if not elf_mode and (clean or build or make_command):
        make_path = make_path or path.join(
            atmel_studio_path, "shellutils", "make.exe")

        def make_caller(command):
            args = ([make_path] + command.split())
            kwargs = dict(cwd=makefile_path, stdout=stdout, stderr=stderr)
            if dry_run:
                print("".join(kwargs.get("cwd", getcwd())) +
                      "> " + " ".join(args))
                return 0
            res = run(args, **kwargs)
            if verbose:
                print(res.stdout.decode())
            return res.returncode
        if make_command:
            returncode = make_caller(make_command)
            if returncode or not atprogram_command:
                return returncode
        if clean:
            returncode = make_caller("clean")
            if returncode:
                return returncode
        if build:
            returncode = make_caller(f"all --jobs {jobs} --output-sync")
            if returncode:
                return returncode
    if not makefile_mode and (erase or program or verify or atprogram_command):
        atprogram_path = atprogram_path or path.join(
            atmel_studio_path, "atbackend", "atprogram.exe")

        def atprogram_caller(command):
            args = ([atprogram_path] + (verbose-1) * ["-v"] + command.split())
            kwargs = dict(stdout=stdout, stderr=stderr)
            if dry_run:
                print(getcwd() + "> " + " ".join(args))
                return 0
            res = run(args, **kwargs)
            if verbose:
                print(res.stdout.decode())
            return res.returncode
        elf_file_path = None if not (program or verify) else project_path if \
            elf_mode else path.join(project_path, configuration,
                                    path.basename(project_path)) + ".elf"
        atprogram_command = atprogram_command or \
            f"-t {tool} -i {interface} -d {device_name}" + \
            (device_sn is not None) * f" -s {device_sn}" + \
            erase * " chiperase" + \
            program * f" program -f {elf_file_path}" + \
            verify * f" verify -f {elf_file_path}" + \
            (verbose >= 3) * " info"
        returncode = atprogram_caller(atprogram_command)
        if returncode:
            atprogram_caller("exitcode")
            return returncode
    return 0
