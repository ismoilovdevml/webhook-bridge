"""Initialize admin user on first startup."""

from sqlalchemy.orm import Session
from ..models.user import User
from ..utils.auth import get_password_hash
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


def init_admin_user(db: Session):
    """Create admin user if it doesn't exist."""
    # Check if any admin user exists
    admin_exists = db.query(User).filter(User.is_admin.is_(True)).first()

    if admin_exists:
        logger.info("Admin user already exists")
        return

    # Create default admin user from environment
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD

    if not admin_password or admin_password == "change-this-password":
        logger.warning(
            "⚠️  DEFAULT ADMIN PASSWORD DETECTED! "
            "Please set ADMIN_PASSWORD in .env for security!"
        )

    # Create admin user
    admin_user = User(
        username=admin_username,
        email=settings.ADMIN_EMAIL,
        hashed_password=get_password_hash(admin_password),
        is_active=True,
        is_admin=True,
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    logger.info(
        f"✅ Admin user created: {admin_username}\n"
        f"   Default password: {admin_password}\n"
        f"   ⚠️  IMPORTANT: Change password after first login!"
    )
