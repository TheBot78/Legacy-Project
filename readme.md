# GeneWeb - Python Version

## 📋 Overview

GeneWeb is an open-source genealogy software with a web interface. This Python version is a modern reimplementation of the original OCaml version, offering the same functionality with a more accessible architecture.

## 🛠️ Technologies Used

### Core Language
- **Python** (≥ 3.8) - Primary development language

### Web Frameworks
- **Flask** (≥ 2.0.0) - Lightweight and flexible web framework
- **Jinja2** (≥ 3.0.0) - Template engine
- **Werkzeug** (≥ 2.0.0) - WSGI utilities

### Database
- **SQLAlchemy** (≥ 1.4.0) - Object-Relational Mapping (ORM)
- Support for SQLite, PostgreSQL, MySQL

### User Interface
- **Click** (≥ 8.0.0) - Command-line interface
- **python-dateutil** (≥ 2.8.0) - Advanced date manipulation

## 🏗️ Architecture

### Project Structure
```
geneweb/
├── bin/                    # Executable scripts
│   ├── gwd.py              # Main web server
│   ├── gwc.py              # Database compiler
│   ├── consang.py          # Consanguinity calculation
│   ├── ged2gwb.py          # GEDCOM import
│   ├── gwb2ged.py          # GEDCOM export
│   └── gwu.py              # Database utilities
├── lib/                    # Python libraries
│   ├── __init__.py
│   ├── adef.py             # Base definitions
│   ├── definitions.py      # Types and structures
│   ├── core/               # Business logic
│   │   ├── consang.py      # Consanguinity calculations
│   │   ├── consang_all.py
│   │   └── gwdb.py         # Database interface
│   ├── db/                 # Data access layer
│   │   ├── dbdisk.py       # Disk storage
│   │   └── driver.py       # Database drivers
│   └── util/               # Utilities
│       ├── calendar.py     # Calendar management
│       ├── date.py         # Date manipulation
│       ├── lock.py         # Lock management
│       ├── mutil.py        # Miscellaneous utilities
│       ├── name.py         # Name processing
│       └── progress_bar.py # Progress bars
├── hd/                     # Web templates and resources
├── plugins/                # Extensions
├── rpc/                    # RPC API
└── test/                   # Unit tests
```


### Main Components

#### 1. Web Server (gwd.py)
- HTTP server based on Flask
- Genealogical route management
- Responsive web interface
- REST API for data access

#### 2. Database (lib/db/)
- Abstraction for different backends
- SQLite support (default)
- Optimized indexing for genealogical searches
- Family relationship management

#### 3. Calculation Engine (lib/core/)
- Consanguinity calculations
- Genealogical algorithms
- Family link management
- Optimizations for large databases

#### 4. Utilities (lib/util/)
- Date management (multiple calendars)
- Name processing (normalization, search)
- File and security utilities

## 🚀 Installation and Usage

### Installation
```bash
# From the project root directory
pip install -e .
```

### Starting the Server
```bash
# Method 1: Via script
python geneweb/bin/gwd.py

# Method 2: Via installed command
gwd

# Method 3: With custom parameters
gwd -p 8080 -d my_database
```

### Command Line Tools
```bash
# Compile a GEDCOM database
ged2gwb file.ged

# Export to GEDCOM
gwb2ged my_database

# Calculate consanguinity
consang my_database

# Database utilities
gwu my_database
```

## 🔧 Configuration

### Environment Variables
- `GENEWEB_DB` - Database name (default: database)
- `GENEWEB_PORT` - Server port (default: 2317)
- `GENEWEB_HOST` - Listen address (default: localhost)
- `GENEWEB_DEBUG` - Debug mode (default: False)

### Configuration Files
- `config.py` - Main configuration
- `database.conf` - Database parameters
- `templates/` - Customizable templates

## 🧪 Testing

```bash
# Run tests
python -m pytest test/

# Tests with coverage
python -m pytest --cov=geneweb test/
```

## 📚 API

### Main Endpoints
- `GET /` - Home page
- `GET /person/{id}` - Individual record
- `GET /family/{id}` - Family record
- `GET /search` - Search
- `POST /api/person` - Create/modify
- `GET /api/stats` - Statistics

## 🔄 Migration from OCaml

The Python version is compatible with databases created by the OCaml version:

```bash
# Import an existing OCaml database
python -c "from geneweb.lib.db import migrate; migrate.from_ocaml('old_database')"
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Develop with tests
4. Submit pull request

### Code Standards
- PEP 8 for Python style
- Type hints recommended
- Documentation for public functions
- Unit tests required

## 📄 License

GPL-2.0-only - See LICENSE file for details.

## 🔗 Useful Links

- [Official GeneWeb Site](https://geneweb.org)
- [Complete Documentation](https://geneweb.tuxfamily.org/wiki/GeneWeb)
- [GitHub Repository](https://github.com/geneweb/geneweb)
- [Community Forum](https://geneweb.org/forum)

---

*This Python version of GeneWeb offers a modern and accessible alternative to the OCaml version, while maintaining the power and functionality of the original software.*