import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import (
    ALLOWED_ORIGINS,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    SPACY_MODEL_PRIMARY,
    SPACY_MODEL_SECONDARY,
    SENTENCE_TRANSFORMER_MODEL,
)
from backend.api.routes import router

logger = logging.getLogger('ats_resume_scorer')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting ATS Resume Analyzer API...')

    logger.info(f'Loading spaCy NLP model: {SPACY_MODEL_PRIMARY}')
    import spacy
    try:
        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
        logger.info(f'Loaded {SPACY_MODEL_PRIMARY}')
    except OSError:
        logger.warning(f'{SPACY_MODEL_PRIMARY} not found - falling back to {SPACY_MODEL_SECONDARY}')
        try:
            app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)
            logger.info(f'Loaded {SPACY_MODEL_SECONDARY} (fallback)')
        except OSError:
            logger.warning(f'{SPACY_MODEL_SECONDARY} not found - falling back to blank("en")')
            app.state.nlp = spacy.blank("en")
            if "sentencizer" not in app.state.nlp.pipe_names:
                app.state.nlp.add_pipe("sentencizer")
            logger.info('Loaded spacy.blank("en")')

    logger.info(f'Loading SentenceTransformer: {SENTENCE_TRANSFORMER_MODEL}')
    try:
        from sentence_transformers import SentenceTransformer
        app.state.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        logger.info(f'Loaded {SENTENCE_TRANSFORMER_MODEL}')
    except Exception as exc:
        logger.warning(f'Could not load SentenceTransformer ({exc}) - using FallbackEmbedder')
        from backend.services.embedder_fallback import FallbackEmbedder
        app.state.embedder = FallbackEmbedder(app.state.nlp)
        logger.info('Loaded FallbackEmbedder')

    logger.info('All models loaded. API is ready to serve requests.')

    yield
    logger.info('shutting down the api!!')

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/redoc'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://resume-ats-system-18ai.vercel.app",
        *ALLOWED_ORIGINS
    ],
    allow_credentials=True,
    allow_methods    = ['*'],
    allow_headers    = ['*'],
)

app.include_router(router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["System"])
async def root_health(request: Request):
    return {
        "status": "healthy",
        "nlp_loaded": getattr(request.app.state, "nlp", None) is not None,
        "embedder_loaded": getattr(request.app.state, "embedder", None) is not None,
    }

# Alias for case-insensitive uvicorn invocation (e.g. backend.main:App)
App = app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'backend.main:app',
        host    = '0.0.0.0',
        port    = 8000,
        reload  = True,     # Auto-restart on code changes (dev only)
    )