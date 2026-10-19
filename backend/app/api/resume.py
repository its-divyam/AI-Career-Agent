from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ResumePatch
from app.utils.dependencies import get_current_user
from app.agents.resume_agent import extract_text, parse_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("")
async def list_resumes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()
    return [
        {
            "resume_id": r.id,
            "target_role": r.target_role,
            "ats_score": r.ats_score,
            "version": r.version,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in resumes
    ]


@router.post("", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    parsed, ats_score, ats_flags = await parse_resume(content, ext)

    resume = Resume(
        user_id=user.id,
        raw_file_url=file.filename,
        parsed_json=parsed,
        ats_score=ats_score,
        target_role=target_role,
    )
    db.add(resume)
    await db.flush()

    # Best-effort RAG indexing: must never fail the upload.
    try:
        from app.rag.store import index_resume

        await index_resume(user.id, str(resume.id), extract_text(content, ext))
    except Exception:
        pass

    return ResumeUploadResponse(
        resume_id=str(resume.id),
        parsed=parsed,
        ats_score=ats_score,
        ats_flags=ats_flags,
    )


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "resume_id": str(resume.id),
        "parsed": resume.parsed_json,
        "ats_score": resume.ats_score,
        "target_role": resume.target_role,
        "version": resume.version,
    }


@router.patch("/{resume_id}")
async def patch_resume(
    resume_id: str,
    body: ResumePatch,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if body.parsed_json is not None:
        resume.parsed_json = body.parsed_json
    if body.target_role is not None:
        resume.target_role = body.target_role

    await db.flush()
    return {"resume_id": str(resume.id), "updated": True}
