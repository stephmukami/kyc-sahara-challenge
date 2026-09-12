import enum


class AppStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Channel(str, enum.Enum):
    app = "app"
    call = "call"
    ussd = "ussd"


class BlockCategory(str, enum.Enum):
    identity = "identity"
    biometric = "biometric"
    compliance = "compliance"
    consent = "consent"
    financial = "financial"


class SessionStatus(str, enum.Enum):
    created = "created"
    in_progress = "in_progress"
    pending_review = "pending_review"
    abandoned = "abandoned"
    completed = "completed"
    approved = "approved"
    rejected = "rejected"


class SessionDecision(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"


class BlockExecutionStatus(str, enum.Enum):
    pending = "pending"
    awaiting_input = "awaiting_input"
    processing = "processing"
    passed = "passed"
    failed = "failed"
    skipped = "skipped"


class ConsentType(str, enum.Enum):
    general_kyc = "general_kyc"
    biometric = "biometric"


class AdminRole(str, enum.Enum):
    super_admin = "super_admin"
    app_admin = "app_admin"


class ActorType(str, enum.Enum):
    admin = "admin"
    user = "user"
    system = "system"
