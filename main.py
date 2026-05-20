from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Scheduler.jobs import start_scheduler 
from routes import employee
from routes.appraisal_cycle import router as cycle_router
from routes.stage import router as stage_router
from routes.parameter import router as parameter_router
from routes.questions import router as question_router
from routes.login import router as login_router
from routes.assignment import router as assignment_router
from routes.employee_allocation import router as employee_allocation_router
from routes.lead_assessment import router as lead_assessment_router
from routes.employee_assessment import router as assessment_router
from routes.edit_appraisal_cycle import router as edit_router
from routes.self_assess_report import router as self_assess_router

app = FastAPI()

@app.on_event("startup")
def startup_event():
    start_scheduler()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

#existing routes
app.include_router(cycle_router)
app.include_router(stage_router)
app.include_router(parameter_router)
app.include_router(employee.router)
app.include_router(question_router)
app.include_router(login_router)
app.include_router(assignment_router)
app.include_router(employee_allocation_router)
app.include_router(lead_assessment_router)
app.include_router(assessment_router)
app.include_router(edit_router)
app.include_router(self_assess_router)
