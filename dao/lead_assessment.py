from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.lead_assessment import LeadAssessmentRating
from models.employee_allocation import EmployeeAllocation
from models.appraisal_cycle import AppraisalCycle
from models.parameters import Parameter
from models.stages import Stage
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


# save lead assessment ratings
def save_lead_assessment_rating(
    db: Session, cycle_id: int, employee_id: int, ratings: list, discussion_date
):
    """
    Save or update lead assessment ratings for an employee in a specific appraisal cycle.
    Args:
        db: Database session
        cycle_id: appraisal cycle ID
        employee_id: employee ID
        ratings: List of dictionaries containing parameter_id and parameter_rating
        discussion_date: Date of discussion
    Returns:
        Success message or error message
    """
    try:
        # Validate if the appraisal cycle is active
        active_cycle = (
            db.query(AppraisalCycle)
            .filter(
                AppraisalCycle.cycle_id == cycle_id, AppraisalCycle.status == "active"
            )
            .first()
        )

        if not active_cycle:
            raise ValueError("The selected appraisal cycle is not active.")

        # Check if the employee is allocated to the cycle
        allocation = (
            db.query(EmployeeAllocation)
            .filter(
                EmployeeAllocation.cycle_id == cycle_id,
                EmployeeAllocation.employee_id == employee_id,
            )
            .first()
        )

        if not allocation:
            raise ValueError("Employee is not allocated to this cycle.")

        # Get the lead assessment stage end date for this cycle
        lead_assessment_stage = (
            db.query(Stage)
            .filter(Stage.cycle_id == cycle_id, Stage.stage_name == "Lead Assessment")
            .first()
        )

        if not lead_assessment_stage:
            raise ValueError("Lead Assessment stage not found for this cycle.")

        # Parse the discussion_date if it's a string
        if isinstance(discussion_date, str):
            try:
                # Try common date formats
                date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]
                parsed_discussion_date = None

                for date_format in date_formats:
                    try:
                        parsed_discussion_date = datetime.strptime(
                            discussion_date, date_format
                        ).date()
                        break
                    except ValueError:
                        continue

                if parsed_discussion_date is None:
                    raise ValueError(
                        f"Could not parse discussion date: {discussion_date}"
                    )
            except Exception as e:
                raise ValueError(f"Invalid discussion date format: {str(e)}")
        else:
            # If discussion_date is already a date object
            parsed_discussion_date = discussion_date

        # Get the stage start and end date and ensure it's a date object
        stage_end_date = lead_assessment_stage.end_date_of_stage
        stage_start_date = lead_assessment_stage.start_date_of_stage

        # Debug
        # print(f"Discussion date: {parsed_discussion_date}, type: {type(parsed_discussion_date)}")
        # print(f"Stage end date: {stage_end_date}, type: {type(stage_end_date)}")

        if not (stage_start_date <= parsed_discussion_date <= stage_end_date):

            # If the discussion date is not within the stage dates, raise an error
            formatted_discussion = parsed_discussion_date.strftime("%d-%m-%Y")
            formatted_end_date = stage_end_date.strftime("%d-%m-%Y")
            formatted_start_date = stage_start_date.strftime("%d-%m-%Y")
            error_msg = f"Discussion date ({formatted_discussion}) must be within the Lead Assessment stage start date ({formatted_start_date}) and end date ({formatted_end_date})."
            print(f"ERROR: {error_msg}")
            db.rollback()
            raise ValueError(error_msg)

        changes_made = False  # Flag to track if any value change in the rating modal

        # save or update ratings, date, specific input
        for rating in ratings:
            param_id = rating["parameter_id"]
            param_rating = rating["parameter_rating"]
            specific_input = rating.get("specific_input", "")

            # Validate if the parameter exists
            parameter = (
                db.query(Parameter).filter(Parameter.parameter_id == param_id).first()
            )
            if not parameter:
                raise ValueError(f"Invalid parameter ID: {param_id}")

            # Validate rating range
            if param_rating < 1 or param_rating > 4:
                raise ValueError(
                    f"Invalid rating for parameter {param_id}. Must be between 1 and 4."
                )

            # Check if a record already exists for this parameter
            existing_rating = (
                db.query(LeadAssessmentRating)
                .filter(
                    LeadAssessmentRating.allocation_id == allocation.allocation_id,
                    LeadAssessmentRating.cycle_id == cycle_id,
                    LeadAssessmentRating.employee_id == employee_id,
                    LeadAssessmentRating.parameter_id == param_id,
                )
                .first()
            )

            if existing_rating:
                # Check if anything has changed
                if (
                    existing_rating.parameter_rating != param_rating
                    or existing_rating.specific_input != specific_input
                    or existing_rating.discussion_date != discussion_date
                ):

                    # Update existing record
                    existing_rating.parameter_rating = param_rating
                    existing_rating.specific_input = specific_input
                    existing_rating.discussion_date = discussion_date
                    changes_made = True  # Mark that an update was done
            else:
                # Insert a new record if it doesn't exist
                new_rating = LeadAssessmentRating(
                    allocation_id=allocation.allocation_id,
                    cycle_id=cycle_id,
                    employee_id=employee_id,
                    parameter_id=param_id,
                    parameter_rating=param_rating,
                    specific_input=specific_input,
                    discussion_date=discussion_date,
                )
                db.add(new_rating)
                changes_made = True  # Mark that a new record was added

        if changes_made:
            db.commit()
            return {"message": "Lead assessment rating saved successfully."}
        else:
            return {"message": "No changes detected."}

    except ValueError as ve:
        db.rollback()
        raise ve

    except SQLAlchemyError:
        db.rollback()
        raise Exception("Database error occurred while saving ratings.")


# historical_report


def get_overall_performance_rating(db: Session, cycle_id: int):
    try:
        parameter = (
            db.query(Parameter)
            .filter(
                Parameter.parameter_title == "Overall Performance Rating",
                Parameter.cycle_id == cycle_id,
            )
            .first()
        )

        if not parameter:
            return []

        ratings = (
            db.query(LeadAssessmentRating)
            .filter(
                LeadAssessmentRating.cycle_id == cycle_id,
                LeadAssessmentRating.parameter_id == parameter.parameter_id,
            )
            .all()
        )

        return ratings

    except SQLAlchemyError as e:
        # Optional: log the error
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching overall performance ratings.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
