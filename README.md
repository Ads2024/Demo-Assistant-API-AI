# SBA Performance Hub 🏭

<div align="center">
  <img src="assets/Snack-Brands-Logo.jpg" alt="KMRD Logo" width="400" />
  <br /><br />

  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python Badge" />
  </a>
  <a href="https://streamlit.io">
    <img src="https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B.svg" alt="Streamlit Badge" />
  </a>
  <a href="https://duckdb.org">
    <img src="https://img.shields.io/badge/DuckDB-0.9.0-DEB887.svg" alt="DuckDB Badge" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-APACHE-red.svg" alt="License Badge" />
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style Badge" />
  </a>
    <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-Enabled-2496ED.svg" alt="Docker Badge" />
  </a>

  <h3><i>AI-powered manufacturing analytics dashboard demo</i></h3>

  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#documentation">Documentation</a>
  </p>
  <hr />
</div>

An AI-powered manufacturing analytics dashboard for Snack Brands Australia, providing real-time insights into operational KPIs and plant performance metrics.

## Features 🚀

- **Interactive Chat Interface**: Natural language queries for manufacturing data analysis
- **Real-time Analytics**: Live monitoring of production metrics and KPIs
- **Manufacturing Metrics**: 
  - Overall Equipment Effectiveness (OEE)
  - Total Effective Equipment Performance (TEEP)
  - Production & Fulfillment Rates
  - Quality & Downtime Analysis
  - Labor Efficiency
- **Data Visualization**: Dynamic charts and metrics visualization
- **Vector Search**: Intelligent querying of manufacturing documentation
- **Responsive Design**: Modern UI with particle.js animations

## Tech Stack 💻

- **Frontend**: Streamlit
- **AI**: OpenAI Assistants API
- **Data Processing**: Python, pandas
- **UI Components**: particles.js
- **Styling**: Custom CSS with glassmorphism effects
- **Docker**: For cloud deployment

## Project Structure 📁

```
sba-performance-hub/
├── .streamlit/          # Streamlit configuration
├── assets/             # Static assets and images
├── src/                # Source code
│   ├── app.py          # Main application
│   ├── layout.yaml     # UI layout configuration
│   ├── styles.py       # CSS styling
│   └── service/        # Backend services
│       ├── ai_service.py   # OpenAI integration
│       └── run.py         # Event handling
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile         # Docker build instructions
├── architecture.md    # System architecture documentation
└── requirements.txt   # Python dependencies
```

## Prerequisites 📋

- Python 3.8+
- OpenAI API key
- Streamlit
- Required Python packages (see requirements.txt)

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sba-performance-hub.git
cd sba-performance-hub
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
### Docker Deployment 🐳

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run manually:
```bash
# Build the image
docker build -t sba-performance-hub .

# Run the container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e ASSISTANT_ID=your_assistant_id \
  -e VECTOR_STORE_ID=your_vector_store_id \
  sba-performance-hub
```

## Environment Setup 🔧

Create `.env` file in project root:
```env
OPENAI_API_KEY=your_api_key
ASSISTANT_ID=your_assistant_id
VECTOR_STORE_ID=your_vector_store_id
```

## Running the Application 🚀

### Local Run
```bash
streamlit run src/app.py
```

### Docker Run
```bash
docker-compose up
```

Access the application at `http://localhost:8501`

<div align="center">
  <img src="assets/Interface_Demo.png" alt="Interface Demo" width="800" />
  <br />
  <i>SBA Performance Hub Interface</i>
</div>

## Documentation 📚

- [System Architecture](architecture.md) - Detailed system design and components
- [API Documentation](docs/API.md) - API reference and usage
- [User Guide](docs/USER_GUIDE.md) - Detailed usage instructions
- [Development Guide](docs/DEVELOPMENT.md) - Setup for developers

## Manufacturing Analytics 📊

### Data Model
- Production Metrics
- Line Performance
- Job Status
- Unit Counts
- Production Stops
- Site Information

### Key Performance Indicators
- OEE Components (Availability, Performance, Quality)
- TEEP Analysis
- Production Fulfillment Rates
- Quality Metrics (Scrap Rate, First Pass Yield)
- Downtime Analysis (MTBF, MTTR)
- Labor Efficiency Metrics

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

[Apache License](LICENSE)

## Maintained By 🔧
*SBA Operations Team*