"""Capture user input to automatically generate YAML file."""
#from importlib.resources import path
from typing import Dict
from typing import List
from pathlib import Path
import os
import typer
import gatoryaml
from gatorconfig import actions_configuration

cli = typer.Typer()



def default_name():
    """Generate default name based on current directory."""
    return os.path.basename(Path.cwd())


#pylint: disable=too-many-arguments
@cli.command()
def cli_input(
    name: str = typer.Option(default_name(), help="The name of the project"),
    brk: bool = typer.Option(False, "--break", help="Enables break"),
    overwrite: bool = typer.Option(False, help="Allows GatorConfig to overwrite existing files"),
    fastfail: bool = typer.Option(False, help="Enables fastfail"),
    gen_readme: bool = typer.Option(False, help="Generates a README file"),
    file: List[str] = typer.Option([], help="""Enter singular file path, can be done
    multiple times"""),
    output_path: Path = typer.Option(Path.cwd(), help="Enter preferred output path"),
    indent: int = typer.Option(4, help="Enter preferred indent"),
    commit_count: int = typer.Option(5, help="Enter preferred minimum amount of commits")
):
    """Gather input from the command line.

    Args:
        name (str, optional): [description]. Defaults to typer.Option(default_name()).
        brk (bool, optional): [description]. Defaults to typer.Option(False, "--break").
        fastfail (bool, optional): [description]. Defaults to typer.Option(False).
        file (List[str], optional): [description]. Defaults to typer.Option([]).
        indent (int, optional): [description]. Defaults to typer.Option(4).
        commit_count (int, optional): [description]. Defaults to typer.Option(5).
    """
    config_dir = output_path.joinpath("config")
    config_dir.mkdir(exist_ok=True)
    if overwrite or not config_dir.joinpath("gatorgrader.yml").exists():
        # Creation of the output variable
        body = get_checks(file)
        #print(files)
        # Creation of the output variable
        header = {
            "name": name,
            "break": brk,
            "fastfail": fastfail,
            "indent": indent,
            "commits": commit_count,
        }
        file_yaml = gatoryaml.dump(header, body)
        output_file(file_yaml, output_path)
    elif config_dir.joinpath("gatorgrader.yml").exists():
        print(f"\"gatorgrader.yml\" already exists within {config_dir}")
    #print(files)
    actions_configuration.create_configuration_file('.github/workflows/grade.yml')
    readme_gen(gen_readme)


def readme_gen(gen_readme: bool):
    """Generate basic README in current directory."""
    if gen_readme is True:
        try:
            with open("README.md", "x", encoding="utf8") as file:
                file.write(
                    "# " + default_name() + "\n" + "\n" +
                    "This is the repository containing the " + default_name() + " assignment."
                    + "\n" + "\n" + "## Using GatorGradle" + "\n" + "\n" +
                    "This assignment utilizes [GatorGrader](https://github.com/GatorEducator/gatorgrader)"
                    " in order to perform automated grading checks." +
                    " To grade your assignment, run the following command in your " +
                    "Docker container or environment containing Gradle:"
                    + "\n" + "\n" + "```" + "\n" + "gradle grade" + "\n" + "```" + "\n"
                )
        except FileExistsError:
            print("Your repository already contains a README.md.")


def output_file(yaml_string: str, output_path: Path):
    """Create and write to file if it doesn't exist, writes to file otherwise.

    Args:
        yaml_string (str): [description]
        output_path (Path): [description]
    """
    pth = Path(output_path / 'config')
    pth.mkdir(exist_ok=True)
    (pth / 'gatorgrader.yml').open('w').write(yaml_string)
    print(f"Wrote file to: {pth}" + "/gatorgrader.yml")


def get_checks(file: List[Path]) -> Dict:
    """Read in checks per file.

    Args:
        file (List[Path]): List of file paths read in from command line.

    Returns:
        Dict: Dictionary of file paths and checks to perform per file.
    """
    files = {}
    for item in file:
        running = True
        check_list = ['--description "Confirm the file exists" ConfirmFileExists',
                      '--description "Make sure there are no TODOs in the file"'
                      ' MatchFileFragment --fragment "TODO" --count 0']
        print(f"These checks are added by default:\n {check_list}")
        print("")
        while running:
            check = input(f"Enter a check for {item} (Press \"Enter\" to move on): ")
            if check.lower() == "":
                running = False
            else:
                check_list.append(check)
        files[item] = list(set(check_list))
    return files

if __name__ == "__main__":
    cli()
