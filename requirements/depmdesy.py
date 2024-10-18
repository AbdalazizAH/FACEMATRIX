import subprocess
import sys
import os


def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error details: {e}")
        sys.exit(1)


def main():

    base_dir = sys.path[0]
    requirements_dir = os.path.join(base_dir)
    print(requirements_dir)

    # Install main dependencies
    dlib = os.path.join(requirements_dir, "dlib-19.24.99-cp312-cp312-win_amd64.whl")
    run_command(f"pip install {dlib}")
    # Install main dependencies
    print("Installing main dependencies...")
    requirements_path = os.path.join(requirements_dir, "requirements.txt")
    run_command(f"pip install -r {requirements_path}")

    # Install face_recognition_models
    print("Installing face_recognition_models...")
    face_recognition_models_dir = os.path.join(
        requirements_dir, "face_recognition_models-master"
    )
    os.chdir(face_recognition_models_dir)
    run_command("python setup.py install")
    os.chdir(os.path.dirname(os.path.dirname(face_recognition_models_dir)))

    print("Installation complete!")


if __name__ == "__main__":
    main()
