"""Final logo set with the approved stepped lettering (Raihat Kufi)."""
import os, sys
sys.argv = sys.argv[:4] + ["/tmp/_unused_letter"]
sys.path.insert(0, os.path.dirname(__file__))
import lettering as Lt
import badges as Bd
from brand import TEAL, TEAL_DARK, CREAM, OCHRE
OUT = os.environ["OUT"]
os.makedirs(OUT, exist_ok=True)
Bd.stacked = Lt.block("رائحة", "أمي", "diagonal")
Bd.OUT = OUT
Bd.save("2-الإطار-المربع", Bd.square())
Bd.save("2-الإطار-المربع-لمسة-حائل", Bd.square(hail=True))
Bd.save("2-الإطار-المربع-معكوس", Bd.square(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
Bd.save("3-الباب-النجدي", Bd.door())
Bd.save("3-الباب-النجدي-لمسة-حائل", Bd.door(hail=True))
Bd.save("3-الباب-النجدي-معكوس", Bd.door(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
print("final ok")
