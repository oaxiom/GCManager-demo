import sys

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from fapi.fapi import app, gcman

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# port 从参数里读取
port = int(sys.argv[1]) if len(sys.argv) > 1 else 7856
# Backend or Doctorend
end_type = sys.argv[2] if len(sys.argv) > 2 else 'Backend'

gcman.set_end_type(end_type)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
