## Configuration file for the app


#Definition of the IMAP servers for the IMAPLoginForm
IMAP_servers = {
    "alumnos.upm.es": "correo.alumnos.upm.es",
    "upm.es": "correo.upm.es",
}

# Definition of the different degrees offered
degrees = [
    "GITST",
    "GIB",
    "MUIT"
]

# Definition of points that are given to the 3 people that complete a milestone first
bonus_position = {
    "1": 500,
    "2": 250,
    "3": 100
}

# Definition of the maximum ammount of points that are given in the milestones against time
max_time_points=1000

# Definition of the points that a second values if a practice is set without a deadline:
# Explantion: each second a certain amount of points will be lost. This parameter sets how
# many points are lost every second
points_per_second=1/10000
