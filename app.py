from flask import Flask, render_template, request
import json

app = Flask(__name__)

with open("universities.json", "r") as file:
    universities = json.load(file)

@app.route("/robots.txt")
def robots():
    return """User-agent: *
Allow: /

Sitemap: https://university-finder-5bcb.onrender.com/sitemap.xml
"""


@app.route("/sitemap.xml")
def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://university-finder-5bcb.onrender.com/</loc>
    </url>
</urlset>
"""

@app.route("/", methods=["GET", "POST"])
def home():

    results = []

    ib_score_input = ""

    if request.method == "POST":
        ib_score_input = request.form["ib_score"]
        ib_score = int(ib_score_input)

        toefl_input = request.form.get("toefl_score")
        ielts_input = request.form.get("ielts_score")

        if toefl_input:
            toefl_score = int(toefl_input)
        else:
            toefl_score = None

        if ielts_input:
            ielts_score = float(ielts_input)
        else:
            ielts_score = None

        field = request.form.get("field")
        country = request.form.get("country")


        print("IB Score:", ib_score)
        print("TOEFL Score:", toefl_score)
        print("IELTS Score:", ielts_score)
        print("Field:", field)
        print("Country:", country)
        print("FORM DATA:", request.form)

        for university in universities:
            for course in university["courses"]:

                english = course.get("english")

                toefl_requirements = (
                    english.get("toefl") if english else None
                )

                ielts_requirements = (
                    english.get("ielts") if english else None
                )

                meets_ib = (
                    course.get("min_ib") is not None
                    and ib_score >= course.get("min_ib")
                )

                meets_toefl = (
                    toefl_score is None
                    or (
                        toefl_requirements is not None
                        and toefl_score >= toefl_requirements["overall"]
                    )
                )

                meets_ielts = (
                    ielts_score is None
                    or (
                        ielts_requirements is not None
                        and ielts_score >= ielts_requirements["overall"]
                    )
                )

                meets_field = (
                    field == "All"
                    or field == course["field"]
                )

                meets_country = (
                    country == "All"
                    or country == university["country"]
                )

                if (
                    meets_ib
                    and meets_toefl
                    and meets_ielts
                    and meets_field
                    and meets_country
                ):
                    results.append({
                        "university": university["name"],
                        "country": university["country"],
                        "course": course["name"],
                        "course_code": course.get("course_code"),
                        "field": course["field"],
                        "min_ib": course.get("min_ib"),

                        "toefl": toefl_requirements,
                        "ielts": ielts_requirements,

                        "min_toefl": (
                            toefl_requirements["overall"]
                            if toefl_requirements
                            else None
                        ),

                        "min_ielts": (
                            ielts_requirements["overall"]
                            if ielts_requirements
                            else None
                        ),

                        "intake": course.get("intake") or [],

                        "official_url": course.get("official_url"),

                        "data_status": course.get("data_status", "verified"),
                        "data_note": course.get("data_note"),
                        "last_verified": course.get("last_verified")
                    })

        print("Results:", results)

    return render_template(
        "index.html",
        results=results,
        ib_score=ib_score_input
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)