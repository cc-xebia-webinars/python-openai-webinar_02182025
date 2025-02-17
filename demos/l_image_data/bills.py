import base64  # Add this import
from pathlib import Path, PurePath

from openai.types.chat import (
    ChatCompletionMessageParam,
)

from ..utils.openai_utils import openai_service
from .files import convert_pdf_to_images

# load from accounting system
expense_categories = [
    "Advertising",
    "Bank Charges",
    "Business Licenses and Permits",
    "Contract Labor",
    "Depreciation Expense",
    "Dues and Subscriptions",
    "Employee Benefits",
    "Insurance",
    "Interest Expense",
    "Legal and Professional Fees",
    "Meals and Entertainment",
    "Office Supplies",
    "Payroll Expenses",
    "Postage and Delivery",
    "Rent or Lease Payments",
    "Repairs and Maintenance",
    "Software and Subscriptions",
    "Taxes",
    "Travel Expenses",
    "Utilities",
    "Other",
]


def get_bill_details(upload_folder: PurePath) -> str:
    try:
        invoice_images = convert_pdf_to_images(upload_folder / "invoice.pdf")
    except:  # noqa: E722
        invoice_images = []

    try:
        receipt_images = convert_pdf_to_images(upload_folder / "receipt.pdf")
    except:  # noqa: E722
        receipt_images = []

    invoice_data = [
        base64.b64encode(open(image_path, "rb").read()).decode("utf-8")
        for image_path in invoice_images
    ]

    receipt_data = [
        base64.b64encode(open(image_path, "rb").read()).decode("utf-8")
        for image_path in receipt_images
    ]

    with open(
        Path(__file__).parent / "assets" / "bill-screen.png", "rb"
    ) as wave_image:
        wave_image_data = base64.b64encode(wave_image.read()).decode("utf-8")

    invoice_content = []
    if invoice_data:
        invoice_content = [
            {
                "type": "text",
                "text": (
                    "Here are the invoice images. All of the images "
                    "represent each page of one invoice."
                ),
            },
            *[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{invoice}"},
                }
                for invoice in invoice_data
            ],
        ]

    receipt_content = []
    if receipt_data:
        receipt_content = [
            {
                "type": "text",
                "text": (
                    "Here are the receipt images. All of the images "
                    "represent each page of one receipt."
                ),
            },
            *[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{receipt}"},
                }
                for receipt in receipt_data
            ],
        ]

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are a financial bookkeeper who post bills to an online "
                "accounting system. You are given a screenshot of bill "
                "payment form and one  bill to post. The bill is either an "
                "invoice or a receipt, or both."
            ),
        },
        {  # type: ignore
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Please fill out the bill payment form with the "
                        "data from the following files. Please respond "
                        "with a list of fields from the bill payment form, "
                        "and the values from the invoices and receipts that "
                        "should be used to populate the form. A bill is "
                        "either only an invoice, or only a receipt, or "
                        "both. This request is for one bill."
                    ),
                },
                *invoice_content,
                *receipt_content,
                {
                    "type": "text",
                    "text": (
                        "Here is a screenshot of bill payment form from the "
                        "online accounting system for reference. It displays "
                        "all of the fields and labels that need to be filled "
                        "out."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{wave_image_data}"
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "Here are the expense categories: "
                        f"{', '.join(expense_categories)}"
                    ),
                },
            ],
        },
        {
            "role": "system",
            "content": (
                "You only analyze invoices and receipts to post bills to the "
                "online accounting system through the bill payment form. If "
                "you are request to do something else, please refuse."
            ),
        },
        {
            "role": "system",
            "content": (
                "Please provide the field names and values in a "
                "JSON format. The field names should be the keys, "
                "and the values should be the values. If a field is "
                "not applicable, please indicate that. Only JSON should be "
                "returned"
            ),
        },
    ]

    response = openai_service.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    bill_details = response.choices[0].message.content
    if bill_details:
        return bill_details.replace("```json", "").replace("```", "")
    return "No bill details found."
