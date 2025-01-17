from sqlalchemy.future import select
from config import get_session
from database.models import Report


async def get_report_settings(chat_id: int):
     async with get_session() as session:
        report = await session.scalar(
            select(Report).filter_by(chat_id=chat_id)
        )
        if report:
            return {
                "enable_reports": report.work,
                "delete_reported_messages": report.delete_reported_messages,
                "report_text_template": report.report_text_template,
            }
        return {
            "enable_reports": False,
            "delete_reported_messages": False,
            "report_text_template": "",
        }


async def save_report_settings(
    chat_id: int,
    enable_reports: bool,
    delete_reported_messages: bool,
    report_text_template: str
):
    async with get_session() as session:
        report = await session.scalar(
            select(Report).filter_by(chat_id=chat_id)
        )
        if report:
            report.work = enable_reports
            report.delete_reported_messages = delete_reported_messages
            report.report_text_template = report_text_template
        else:
            report = Report(
                chat_id=chat_id,
                work=enable_reports,
                delete_reported_messages=delete_reported_messages,
                report_text_template=report_text_template,
            )
            session.add(report)
        await session.commit()