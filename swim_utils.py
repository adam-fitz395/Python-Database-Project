from statistics import mean


import hfpy_utils

FOLDER = "uploaded/"


def convert2hundreths(timestring):
    """Given a string which represents a time, this function converts the string
    to a number (int) representing the string's hundredths of seconds value, which is
    returned.
    """
    if ":" in timestring:
        mins, rest = timestring.split(":")
        secs, hundredths = rest.split(".")
    else:
        mins = 0
        secs, hundredths = timestring.split(".")

    return int(hundredths) + (int(secs) * 100) + ((int(mins) * 60) * 100)


def build_time_string(num_time):
    """ """
    secs, hundredths = str(round(num_time / 100, 2)).split(".")
    mins = int(secs) // 60
    seconds = int(secs) - mins * 60
    return f"{mins}:{seconds}.{hundredths}"


def get_swimmers_data(filename):
    """ """
    name, age, distance, stroke = filename.removesuffix(".txt").split("-")
    with open(FOLDER + filename) as fh:
        data = fh.read()
    times = data.strip().split(",")
    converts = []  # empty list
    for t in times:
        converts.append(convert2hundreths(t))
    average = build_time_string(mean(converts))

    return name, age, distance, stroke, times, converts, average


def produce_bar_chart(fn):
    """Given the name of a swimmer's file, produce a HTML/SVG-based bar chart.

    Save the chart to the CHARTS folder. Return the path to the bar chart file.
    """
    swimmer, age, distance, stroke, times, converts, average = get_swimmers_data(fn)
    from_max = max(converts) + 50
    times.reverse()
    converts.reverse()
    title = f"{swimmer} (Under {age}) {distance} {stroke}"
    header = f"""<!DOCTYPE html>
                    <html>
                        <head>
                            <title>{title}</title>
                        </head>
                        <body>
                            <h3>{title}</h3>"""
    body = ""
    for n, t in enumerate(times):
        bar_width = hfpy_utils.convert2range(converts[n], 0, from_max, 0, 350)
        body = (
            body
            + f"""
                            <svg height="30" width="400">
                                <rect height="30" width="{bar_width}" style="fill:rgb(0,0,255);" />
                            </svg>{t}<br />"""
        )
    footer = f"""
                            <p>Average time: {average}</p>
                        </body>
                    </html>"""
    page = header + body + footer
    save_to = f"{fn.removesuffix('.txt')}.html"
    with open(save_to, "w") as sf:
        print(page, file=sf)

    return save_to
