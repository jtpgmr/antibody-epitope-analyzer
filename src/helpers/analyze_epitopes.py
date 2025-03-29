import subprocess

from src.models import *

def exec_muscle_command(input_fasta, output_alignment) -> str:
    """Run MUSCLEv5.2 to perform multiple sequence alignment."""
    command = [muscle_exe, "-align", input_fasta, "-output", output_alignment]

    result = subprocess.run(command, capture_output=True, text=True)
    print(555, result)
    if result.returncode == 0:
        logger.info("MUSCLE alignment complete")
        # successful result outputs are being returned in the stderr
        return result.stderr
    else:
        logger.fatal(f"Error running MUSCLE: {result.stderr}")
        raise Exception("Muscle sequence alignment failed")
