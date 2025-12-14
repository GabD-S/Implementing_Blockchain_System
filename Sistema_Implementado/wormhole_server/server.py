import asyncio
import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SendReq(BaseModel):
    filename: str
    directory: Optional[str] = None

class RecvReq(BaseModel):
    code: str
    confirm: bool = True

async def run_command(cmd:list[str], input_text: Optional[str] = None):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE if input_text else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    if input_text:
        assert proc.stdin is not None
        proc.stdin.write(input_text.encode())
        await proc.stdin.drain()
        proc.stdin.close()
    stdout, stderr = await proc.communicate()
    return proc.returncode == 0, stdout.decode(), stderr.decode()

@app.post('/send')
async def send_file(req: SendReq):
    # Ensure wormhole is available
    await run_command(["pip", "install", "magic-wormhole", "--break-system-packages"])  # ignore result

    filename = req.filename
    if req.directory:
        filename = os.path.join(req.directory, filename)
    ok, out, err = await run_command(["wormhole", "send", filename])
    return {"ok": ok, "stdout": out, "stderr": err}

@app.post('/receive')
async def receive_file(req: RecvReq):
    # Auto-confirm 'y' if required
    input_text = None
    if req.confirm:
        input_text = "y\n"
    ok, out, err = await run_command(["wormhole", "receive", req.code], input_text=input_text)
    # Try to parse the saved path from stdout
    saved_path = None
    for line in out.splitlines():
        if "Received file written to:" in line:
            saved_path = line.split(":",1)[1].strip()
            break
    return {"ok": ok, "stdout": out, "stderr": err, "path": saved_path}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8090)
