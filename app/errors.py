from __future__ import annotations

class AppError(Exception): 
    def __init__(self,message:str, field :str|None = None): 
        self.message = message
        self.field = field
        super().__init__(message)
        
class ValidationError(AppError): 
    pass 
class NotFoundError(AppError): 
    pass
class InvalidStateError(AppError):
    pass

