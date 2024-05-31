
from . import prepare,tools
from .states import splash, putting, swinging, spectating
from .states import view_scorecard, hole_start, ball_placement


def main():
    run_it = tools.Control(prepare.ORIGINAL_CAPTION)
    state_dict = {
            "SPLASH": splash.Splash(),
            "PUTTING": putting.Putting(),
            "SWINGING": swinging.Swinging(),
            "SPECTATING": spectating.Spectating(),
            "SCORECARD": view_scorecard.ViewScorecard(),
            "HOLESTART": hole_start.HoleStart(),
            "BALLPLACEMENT": ball_placement.BallPlacement()
            }
    run_it.setup_states(state_dict, "SPLASH")
    run_it.main()
