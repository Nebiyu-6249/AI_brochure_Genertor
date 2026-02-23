from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.schemas import BrochureRequest, BrochureResponse
from app.services.brochure_service import generate_brochure

load_dotenv(override=False)

app = FastAPI(title="AI Brochure Generator", version="1.0.0")

templates = Jinja2Templates(directory="templates")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=HTMLResponse)
def generate_ui(
    request: Request,
    company_name: str = Form(...),
    website_url: str = Form(...),
    tone: str = Form(default="professional"),
):
    try:
        brochure_md, sources = generate_brochure(company_name, website_url, tone=tone)
        try:
            import markdown as mdlib  # type: ignore
            brochure_html = mdlib.markdown(brochure_md)
        except Exception:
            brochure_html = "<pre>" + brochure_md.replace("<", "&lt;").replace(">", "&gt;") + "</pre>"

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "company_name": company_name,
                "website_url": website_url,
                "tone": tone,
                "brochure_markdown": brochure_md,
                "brochure_html": brochure_html,
                "sources": sources,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": str(e)},
            status_code=500,
        )


@app.post("/api/brochure", response_model=BrochureResponse)
def api_brochure(payload: BrochureRequest):
    brochure_md, sources = generate_brochure(payload.company_name, payload.website_url, tone=payload.tone)
    try:
        import markdown as mdlib  
        brochure_html = mdlib.markdown(brochure_md)
    except Exception:
        brochure_html = brochure_md
    return BrochureResponse(brochure_markdown=brochure_md, brochure_html=brochure_html, sources=sources)
