from sqlalchemy.orm import Session
from models.lead_assessment import LeadAssessmentRating
from models.employee_allocation import EmployeeAllocation
from models.appraisal_cycle import AppraisalCycle
from models.parameters import Parameter
from sqlalchemy.exc import SQLAlchemyError


# To save the ratings given by the the lead during lead assessment stage
def save_lead_assessment_rating(
    db: Session, cycle_id: int, employee_id: int, ratings: list, discussion_date
):
    try:
        active_cycle = (
            db.query(AppraisalCycle)
            .filter(
                AppraisalCycle.cycle_id == cycle_id, AppraisalCycle.status == "active"
            )
            .first()
        )

        if not active_cycle:
            raise ValueError("The selected appraisal cycle is not active.")

        allocation = (
            db.query(EmployeeAllocation)
            .filter(
                EmployeeAllocation.cycle_id == cycle_id,
                EmployeeAllocation.employee_id == employee_id,
            )
            .first()
        )

        if not allocation:
            raise ValueError("No allocation found")

        changes_made = False

        for rating in ratings:
            parameter = (
                db.query(Parameter)
                .filter(Parameter.parameter_id == rating["parameter_id"])
                .first()
            )
            if not parameter:
                raise ValueError(f"Invalid parameter ID: {rating['parameter_id']}")

            if rating["parameter_rating"] < 1 or rating["parameter_rating"] > 4:
                raise ValueError(
                    f"Invalid rating for parameter {rating['parameter_id']}. Must be between 1 and 4."
                )

            existing_rating = (
                db.query(LeadAssessmentRating)
                .filter(
                    LeadAssessmentRating.cycle_id == cycle_id,
                    LeadAssessmentRating.employee_id == employee_id,
                    LeadAssessmentRating.parameter_id == rating["parameter_id"],
                )
                .first()
            )

            if existing_rating:
                if (
                    existing_rating.parameter_rating != rating["parameter_rating"]
                    or existing_rating.specific_input
                    != rating.get("specific_input", "")
                    or existing_rating.discussion_date != discussion_date
                ):

                    existing_rating.parameter_rating = rating["parameter_rating"]
                    existing_rating.specific_input = rating.get("specific_input", "")
                    existing_rating.discussion_date = discussion_date
                    changes_made = True
            else:
                new_rating = LeadAssessmentRating(
                    allocation_id=allocation.allocation_id,
                    cycle_id=cycle_id,
                    employee_id=employee_id,
                    parameter_id=rating["parameter_id"],
                    parameter_rating=rating["parameter_rating"],
                    specific_input=rating.get("specific_input", ""),
                    discussion_date=discussion_date,
                )
        db.add(new_rating)
        changes_made = True

        if changes_made:
            db.commit()
            return {"message": "Lead assessment rating updated successfully."}
        else:
            return {"message": "No changes detected."}

    except ValueError as ve:
        db.rollback()
        raise ve

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Database error occurred while saving ratings.")
