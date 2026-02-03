import uvicorn
import os

if __name__ == "__main__":
    # Roda o servidor Uvicorn apontando para a pasta src, arquivo app, objeto app
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)