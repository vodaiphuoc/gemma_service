from common.schemas import (
    ExtractModelResult, 
    Education,
    Experience
)
from .extract import pdf2imgs, read_image
from PIL import Image
import os

# Example
_PROMPT_EXAMPLE = ExtractModelResult(
    name = "Michael Seymour",
    email= "example@cvmaker.uk",
    phone_number="+441214960508",
    education= [
            Education(
                university_name = "Imperial College London, UK",
                degree_type = "Master",
                major = "Computer Science",
                from_time="",
                to_time="2017",
                gpa=None
            ),
            Education(
                university_name = "University of Manchester, UK",
                degree_type = "Bachelor",
                major = "Computer Science",
                from_time="",
                to_time="2014",
                gpa=None
            )
        ],
    experiences= [
        Experience(
            company_name="EZ Tech Solution",
            job_position="Senior Software Enginner",
            from_time="2020",
            to_time="present",
            responsibilities=[
"""Lead a development team using React and Python. Participate in Agile methods, contributing to sprint planning, 
backlog grooming, and sprint retrospectives. Collaborate with cross-functional teams to design and implement 
scalable microservices architecture. Conduct code reviews and mentor junior developers, fostering continuous 
learning and code quality improvement""",
"""Successfully led a cutting-edge web application, revamping user interface, resulting in a remarkable 65% increase 
in user engagement and a boost in customer satisfaction""",
"""Led team to design and implement a scalable microservices architecture, seamlessly
integrating cross-functional teams and achieving an impressive 30% reduction in system
downtime."""
            ],
            technologies=[""],
            projects=[""],
            awards=[""]
        ),
        Experience(
            company_name="FC Software Solutions",
            job_position="Software Enginner",
            from_time="2018",
            to_time="2020",
            responsibilities=[
"""Developed and maintained backend systems for a cloud-based SaaS platform, prioritising system stability 
and efficiency to deliver a high-performance user experience. Collaborated closely with UI/UX designers to build responsive 
web applications, ensuring seamless user experiences across various devices and screen sizes""",
"""Improved system performance by optimising backend systems, achieving 15% reduction in
response time, leading to a more responsive and satisfying user experience.""",
"""Successfully implemented unit tests and automated integration tests, resulting in 20% increase
in code coverage and a significant reduction in production defects.""",
"""Enhanced the continuous integration and deployment pipeline, enabling faster and more
reliable releases, ensuring quicker updates and improved platform stability."""
            ],
            technologies=[""],
            projects=[""],
            awards=[""]
        )
    ],
    tech_stacks=[
        "Web Technologies: HTML, CSS, JavaScript, React", 
        "Database: MySQL, MongoDB",
        "Version Control: Git",
        "Cloud Services: Amazon Web Services (AWS), Microsoft Azure",
        "Operating Systems: Windows, Linux, macOS",
        "Software Development Tools: IntelliJ, Eclipse, Visual Studio Code",
        "Programming Languages: Python, Java, C++"
    ],
    personal_projects=[""],
    certifications = [
        "AWS Certified Developer - Associate",
        "Certified Scrum Master (CSM), LearningLean"
    ]
).model_dump_json(indent=2)

EXAMPLE_CONTENTS = [{
            "type": "text",
            "text": "\n<examples>\nBelow is an example of image inputs and its output:\n--- **EXAMPLE BEGINS** ---\nExample input images:\n"
}]
EXAMPLE_CONTENTS.extend([{
        "type": "image",
        "image": read_image(_img_path)
    }
    for _img_path in pdf2imgs(pdf_path=os.path.join(
        os.path.dirname(__file__).replace("components","examples"), 
        "example.pdf"
    )
    )
])
EXAMPLE_CONTENTS.append({
    "type": "text",
    "text": f"\nDesire example Output:\n```json\n{_PROMPT_EXAMPLE}\n```\n--- **EXAMPLE ENDS** ---\n"
})
