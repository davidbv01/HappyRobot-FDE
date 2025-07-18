# HappyRobot FDE API

## What is this API for?

HappyRobot FDE API is a backend service for freight dispatch and carrier management. It provides endpoints to:
- Verify carrier MC numbers with FMCSA integration
- Find and manage available freight loads
- Finalize and record negotiation calls (deals and no-deals)
- Retrieve call history and statistics

This API is designed for logistics, dispatch, and digital freight platforms that need to automate and track carrier interactions, load assignments, and negotiation outcomes.

---

## Development Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd HappyRobot-FDE
```

### 2. Create a virtual environment
```bash
python -m venv env
```

### 3. Activate the environment
- **Windows:**
  ```bash
  .\env\Scripts\activate
  ```
- **Linux/macOS:**
  ```bash
  source env/bin/activate
  ```

### 4. Copy and configure environment variables
```bash
cp .env.docker .env
# Edit .env and set your FMCSA_API_KEY and other secrets
```

### 5. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Run the development server
```bash
uvicorn main:app --reload
```

- Access the API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

---

## Production Deployment (Cloud, Docker)

### 1. Build and run with Docker Compose

```bash
# Set your FMCSA API key (and any other secrets)
export FMCSA_API_KEY=your_actual_fmcsa_api_key_here

# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 2. Build and run with Docker only

```bash
# Build the image
docker build -t happyrobot-fde .

# Run the container
docker run -d \
  --name happyrobot-fde-api \
  -p 8000:8000 \
  -e FMCSA_API_KEY=your_actual_fmcsa_api_key_here \
  -v $(pwd)/temp:/app/temp \
  happyrobot-fde
```

### 3. Environment Variables
- `FMCSA_API_KEY` (required): Your FMCSA API key for MC verification
- `API_KEYS`: Custom API keys (default: demo keys)
- `DEBUG`: Enable debug mode (default: false)
- `APP_NAME`, `APP_VERSION`: Optional metadata

### 4. Data Persistence
- Call data is stored in `/app/temp` inside the container
- Mount a volume to persist data: `-v $(pwd)/temp:/app/temp`

### 5. Health Check
- The container exposes `/health` for monitoring

### 6. Scaling
- For high-traffic, use Docker Compose scaling or a cloud orchestrator

---

## API Overview

- **GET** `/carriers/{mc_number}`: Verify carrier MC number
- **GET** `/loads/best`: Get best available load
- **POST** `/deals`: Record a closed deal
- **POST** `/calls`: Record a call (no deal, rejected, etc.)
- **GET** `/calls`: Retrieve all calls and statistics

See `/docs` for full OpenAPI documentation.

---

## Security Notes
- Change default API keys in production
- Never commit your `.env` with real secrets
- Use HTTPS and a reverse proxy in production

---

## License
MIT (or your license here) 