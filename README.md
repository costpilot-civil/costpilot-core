# CostPilot Core

`costpilot-core` contains the reusable core logic and shared domain models used by CostPilot.

The package is designed to be independent from the frontend, backend API, and database infrastructure.

## Responsibilities

The core package is responsible for:

- Shared domain models
- Tender item representation
- Material classification and structured attribute extraction
- Text normalization and text building
- Embedding model interfaces and implementations
- Reranker model interfaces and implementations
- Shared matching-related data models

The package should contain logic that can be reused by different CostPilot components without depending on a specific runtime environment.

## Boundaries

`costpilot-core` does **not** handle:

- API endpoints
- Project management
- Database connections or SQL queries
- Database schema or migrations
- Commodity data import
- Tender file upload workflows
- Retrieval orchestration
- Match pipeline orchestration
- Result persistence
- Frontend logic

These responsibilities belong to `costpilot-backend`, `costpilot-database`, or `costpilot-frontend`.

## Main Modules

### Tender

Shared models for tender data.

Example:

- `TenderDocument`
- `TenderItem`

A `TenderItem` represents a single position inside a tender document and contains information such as:

- position number
- short text
- long text
- quantity
- unit

### Material

Material understanding and structured information extraction.

This module includes functionality for:

- material classification
- keyword matching
- attribute extraction
- material templates
- normalized material representation

Example attributes may include:

- material type
- strength class
- exposure class
- grain size
- steel grade

### Text

Shared text-processing utilities used by retrieval and ranking.

Typical functionality includes:

- text normalization
- building searchable text from tender items
- building searchable text from commodities

### Embedding

Reusable embedding model abstractions and implementations.

The embedding module converts text into vector representations used by the backend for vector retrieval.

### Reranking

Reusable reranker model abstractions and implementations.

The reranker assigns relevance scores to a query and a set of candidate texts.

The backend remains responsible for candidate selection, ranking workflow, and match decisions.

### Matching Models

Shared data structures used during the matching process, for example:

- match candidates
- match status
- matching-related DTOs

These models describe data exchanged between components but do not control the matching workflow itself.

## Architecture

```text
costpilot-core
      ▲
      │
      ├── costpilot-backend
      │
      └── costpilot-database
```

Both backend and database components may depend on costpilot-core.

costpilot-core must not depend on either of them.

## Design Principle

The package should remain:
- reusable
- infrastructure-independent
- database-independent
- API-independent
- focused on domain logic and shared models