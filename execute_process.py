"""
Class for executing system sub-processes asynchronously.
"""
import asyncio
import re


class Process:
    '''
    Help to define the methdo for execute system sub-process
    '''

    def __init__(self, params):
        
        if not isinstance(params, list):
            raise TypeError("params must be a list of command arguments")

        self.params = params

    async def see_result_process(self, description=None, timeout=30):
        '''
        This method allow see the result in real time
        '''
        output_str = None
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        if description:
            print(f"Executing process: {description}...")
        if not self.params:
            return None, None
        try:
            process = await asyncio.create_subprocess_exec(
                *self.params,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,)

            async with asyncio.timeout(timeout):
                output_str = ""
                async for line in process.stdout:
                    decoded_line = line.decode().strip()
                    no_ansi = ansi_escape.sub('', decoded_line)
                    no_space = re.sub(r'\s+', ' ', no_ansi).strip()
                    output_str += f"{no_space} \n"
                    print(decoded_line)

        except asyncio.TimeoutError:
            print("Time out")

        except RuntimeError:
            print("A RuntimeError ocurred")

        finally:
            if process.returncode is None:
                process.terminate()
                await process.wait()

        if process.returncode != 0:
            print(
                f"Error when executing the subprocess,"
                f"{process.returncode}\n")
            return None, output_str

        return True, output_str

    async def see_end_result_process(self, description=None):
        """
        This method waits for the subprocess to finish and returns the final
        result.
        """
        if description:
            print(f"Executing process: {description}...")
        if not self.params:
            return None, None
        success = None
        stdout_response = None
        stdout_result = None
        stderr_result = None
        try:

            process = await asyncio.create_subprocess_exec(
                *self.params,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,)

            stdout, stderr = await process.communicate()
            stdout_result = stdout.decode()
            stderr_result = stderr.decode()

            # await to finish the sub process
            await process.wait()

            # check if there are no errors when executing the sub-process

        except RuntimeError:
            print("A RuntimeError occurred")

        except KeyboardInterrupt:
            print("An error occurred")

        except asyncio.CancelledError:
            print("An error occurred")

        finally:
            if process.returncode == 0:
                print("Subprocess executed correctly")
            else:
                print(
                    f"Error when executing the subprocess "
                    f"{process.returncode if process.returncode is not None else ''}")

            if process.returncode == 0:
                success = True
                if stdout_result:
                    print(f'[stdout]\n{stdout_result}')
                    stdout_response = stdout_result

            if stderr_result:
                print(f'[stderr]\n{stderr_result}')

        return success, stdout_response
