import os
import skbuild


def main():
    # Optional: Set the CONDA_PREFIX environment variable to the path of your conda environment
    # Useful if CMAKE can't find the conda environment
    cmake_args = []
    if env_conda := os.getenv("CONDA_PREFIX"):
        cmake_args.append(f"-DCONDA_PREFIX={env_conda}")

    # Find all python modules in the src directory
    # package_list = find_namespace_packages(where='sleep')
    # print("Found packages:", package_list)

    # Define the python modules to be built
    skbuild.setup(
        name="sleep",
        version="0.0.0",
        description="Python Wrapper for BusySleep",
        packages=["sleep"],
        package_dir={"sleep": "sleep_src"},
        python_requires=">=3.8",
        cmake_args=cmake_args,
    )


if __name__ == "__main__":
    main()
