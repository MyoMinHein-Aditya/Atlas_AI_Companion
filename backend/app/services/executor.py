import asyncio
import logging

logger = logging.getLogger("atlas-backend")

# List of dangerous commands that trigger strict blocking
DANGEROUS_KEYWORDS = [
    "rm ", "rmdir", "del ", "erase", "format ", "mkfs", "dd ",
    "partition", "fdisk", "shutdown", "reboot", "init 0", "init 6",
    "wmic ", "sc delete", "reg delete", "net user", "net share",
    "format-volume", "remove-item", "clear-disk"
]

async def execute_command(command: str) -> str:
    """Runs a shell command asynchronously and returns stdout/stderr logs."""
    logger.info(f"Executing subprocess command: '{command}'")
    try:
        # Spawn async subprocess shell
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        stdout_decoded = stdout.decode('utf-8', errors='replace').strip()
        stderr_decoded = stderr.decode('utf-8', errors='replace').strip()

        outputs = []
        if stdout_decoded:
            outputs.append(stdout_decoded)
        if stderr_decoded:
            outputs.append(f"Stderr:\n{stderr_decoded}")

        return "\n".join(outputs) if outputs else "Command finished with no output."
    except Exception as e:
        logger.error(f"Execution failed for command '{command}': {str(e)}")
        return f"Execution error: {str(e)}"

def is_command_safe(command: str) -> bool:
    """Scans command string against dangerous keywords."""
    cmd_lower = command.lower().strip()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in cmd_lower:
            logger.warning(f"Safety Gate Triggered: Command '{command}' matched blacklist keyword '{keyword}'")
            return False
    return True
