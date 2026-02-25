"""Analysis endpoints: POST /analyze and POST /batch-analyze."""

from fastapi import APIRouter, HTTPException, Request

from lensforge.schemas.request import AnalyzeRequest, BatchAnalyzeRequest
from lensforge.schemas.response import AnalyzeResponse, BatchAnalyzeResponse

router = APIRouter()


def _get_pipeline(request: Request):
    return request.app.state.container.analysis_pipeline()


def _get_loader(request: Request):
    return request.app.state.container.image_loader()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    """Analyze a single image."""
    pipeline = _get_pipeline(request)
    loader = _get_loader(request)

    try:
        if req.image_base64:
            image = loader.load_base64(req.image_base64)
        elif req.image_url:
            image = loader.load_url(req.image_url)
        else:
            raise HTTPException(status_code=400, detail="No image provided")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return pipeline.analyze(image)


@router.post("/batch-analyze", response_model=BatchAnalyzeResponse)
def batch_analyze(req: BatchAnalyzeRequest, request: Request) -> BatchAnalyzeResponse:
    """Analyze multiple images."""
    pipeline = _get_pipeline(request)
    loader = _get_loader(request)
    results: list[AnalyzeResponse] = []

    for item in req.images:
        try:
            if item.image_base64:
                image = loader.load_base64(item.image_base64)
            elif item.image_url:
                image = loader.load_url(item.image_url)
            else:
                results.append(
                    AnalyzeResponse(status="error", reason="No image provided", disclaimer="")
                )
                continue
            results.append(pipeline.analyze(image))
        except ValueError as exc:
            results.append(AnalyzeResponse(status="error", reason=str(exc), disclaimer=""))

    return BatchAnalyzeResponse(results=results)
