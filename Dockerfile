# Dockerfile
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o ficheiro de dependências
COPY requirements_utf8.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements_utf8.txt

# Copia todo o código da aplicação
COPY ./app ./app

# Expõe a porta que o Uvicorn irá usar
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]