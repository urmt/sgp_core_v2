"""RD-022 Explainer for 5th Graders: The Mystery of the Sand Pile Score

Core visual thesis:
"We gave a pile of sand a health score. We tested 8 ways to measure it.
All 8 agreed the score is real. But we still don't know what it means."
"""

from manim import *
import numpy as np


class SandPileExplainer(Scene):
    """Main explainer scene: 5 parts, ~60 seconds total."""

    def setup(self):
        self.rng = np.random.default_rng(7)
        self.colors = [RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, PURPLE, PINK]

    def construct(self):
        self.scene_title()
        self.scene_what_is_c()
        self.scene_the_question()
        self.scene_eight_rulers()
        self.scene_the_result()
        self.scene_the_mystery()

    # ─── SCENE 1: Title ───

    def scene_title(self):
        title = Text("The Mystery of the Sand Pile Score", font_size=42, color=YELLOW)
        subtitle = Text(
            "How we tested if a math score is real",
            font_size=24, color=GRAY, font="Sans"
        )
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ─── SCENE 2: What is C? ───

    def scene_what_is_c(self):
        # Title
        label = Text("What is a Sand Pile Score?", font_size=36, color=BLUE)
        label.to_edge(UP, buff=0.5)
        self.play(Write(label))

        # Draw sand grains as circles
        grains = VGroup()
        for i in range(30):
            x = self.rng.uniform(-3.5, 3.5)
            y = self.rng.uniform(-2.5, 0.5)
            r = self.rng.uniform(0.15, 0.3)
            c = Circle(radius=r, color=ORANGE, fill_opacity=0.7)
            c.move_to([x, y, 0])
            grains.add(c)

        self.play(LaggedStart(*[GrowFromCenter(g) for g in grains], lag_ratio=0.03), run_time=1.5)

        # Score label
        score_box = Rectangle(width=2, height=0.8, color=GREEN, fill_color=GREEN, fill_opacity=0.2)
        score_box.to_edge(RIGHT, buff=1).shift(UP * 1)
        score_text = Text("Score: 0.47", font_size=28, color=GREEN)
        score_text.move_to(score_box.get_center())
        score_group = VGroup(score_box, score_text)

        arrow = Arrow(score_box.get_left(), RIGHT * 0.5 + UP * 0.5, color=WHITE)

        self.play(Create(score_box), Write(score_text), run_time=0.8)
        self.play(Create(arrow))

        # Explanation
        explain = Text(
            "We count how the grains move together.\n"
            "High score = they move in sync.\n"
            "Low score = they move randomly.",
            font_size=20, color=WHITE, font="Sans"
        )
        explain.to_edge(DOWN, buff=0.6)
        self.play(Write(explain), run_time=2)
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])

    # ─── SCENE 3: The Question ───

    def scene_the_question(self):
        q = Text(
            "Is this score REAL?",
            font_size=48, color=YELLOW
        )
        self.play(Write(q), run_time=1)
        self.wait(1)

        sub = Text(
            "Or did we just measure it wrong?",
            font_size=28, color=GRAY, font="Sans"
        )
        sub.next_to(q, DOWN, buff=0.5)
        self.play(FadeIn(sub), run_time=0.8)
        self.wait(2)

        # Show a ruler breaking
        ruler = Rectangle(width=6, height=0.4, color=BLUE, fill_opacity=0.3)
        ruler.next_to(sub, DOWN, buff=0.8)
        tick_marks = VGroup()
        for i in range(13):
            x = ruler.get_left()[0] + i * (6 / 12)
            tick = Line([x, ruler.get_top()[1], 0], [x, ruler.get_top()[1] + 0.2, 0], color=WHITE)
            tick_marks.add(tick)

        ruler_label = Text("Our measurement tool", font_size=16, color=BLUE)
        ruler_label.next_to(ruler, DOWN, buff=0.2)

        self.play(Create(ruler), Create(tick_marks), Write(ruler_label))
        self.wait(1)

        # Crack the ruler
        crack = Line(
            ruler.get_center() + LEFT * 0.3 + UP * 0.2,
            ruler.get_center() + RIGHT * 0.3 + DOWN * 0.2,
            color=RED, stroke_width=4
        )
        self.play(Create(crack), run_time=0.3)
        self.play(ruler.animate.shift(DOWN * 0.1 + LEFT * 0.1), run_time=0.2)
        self.wait(1.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects])

    # ─── SCENE 4: Eight Rulers ───

    def scene_eight_rulers(self):
        title = Text("So we tried 8 different rulers", font_size=34, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # 8 ruler labels
        rulers = VGroup()
        names = ["E0\nBaseline", "E1\nShort\nWindow", "E2\nLong\nWindow", "E3\n5 Bins",
                 "E4\n20 Bins", "E5\nShifted\nBins", "E6\nBootstrap", "E7\nLeave\nOne Out"]

        for i in range(8):
            box = Rectangle(width=1.4, height=1.8, color=self.colors[i],
                           fill_color=self.colors[i], fill_opacity=0.15)
            label = Text(names[i], font_size=13, color=self.colors[i], font="Sans")
            label.move_to(box.get_center())
            group = VGroup(box, label)
            group.shift(RIGHT * (i * 1.7 - 5.95))
            group.shift(DOWN * 0.3)
            rulers.add(group)

        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.3) for r in rulers], lag_ratio=0.1), run_time=2)
        self.wait(1)

        # All arrows point to same conclusion
        conclusion = Text(
            "All 8 say the SAME thing:\n"
            "The score predicts how well\n"
            "the sand pile bounces back!",
            font_size=22, color=GREEN, font="Sans"
        )
        conclusion.to_edge(DOWN, buff=0.5)

        arrows = VGroup()
        for r in rulers:
            a = Arrow(r.get_bottom(), conclusion.get_top(), color=GRAY, stroke_width=1.5, buff=0.15)
            arrows.add(a)

        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.05), run_time=1)
        self.play(Write(conclusion), run_time=1.5)
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])

    # ─── SCENE 5: The Result ───

    def scene_the_result(self):
        title = Text("The Result", font_size=42, color=GREEN)
        title.to_edge(UP, buff=0.6)
        self.play(Write(title))

        # Show "8/8" big
        big = Text("8 out of 8", font_size=60, color=GREEN)
        self.play(Write(big), run_time=1)
        self.wait(0.5)

        agree = Text("AGREE!", font_size=48, color=YELLOW)
        agree.next_to(big, DOWN, buff=0.4)
        self.play(Write(agree), run_time=0.8)
        self.wait(1)

        # Show a bar chart: all bars go down (restoration)
        bar_title = Text("Prediction: Higher Score → Worse Recovery", font_size=18, color=GRAY, font="Sans")
        bar_title.shift(DOWN * 0.3)
        self.play(FadeIn(bar_title))

        # Pre-defined R² values from RD-022 (real data!)
        r2_vals = [0.320, 0.218, 0.289, 0.439, 0.096, 0.326, 0.314, 0.323]
        bars = VGroup()
        for i in range(8):
            h = r2_vals[i] * 5  # scale to visible
            bar = Rectangle(width=0.5, height=max(h, 0.1), color=self.colors[i], fill_opacity=0.7)
            bar.move_to(RIGHT * (i * 0.7 - 2.45) + DOWN * (h / 2 + 1.0))
            bars.add(bar)

        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08), run_time=2)

        # Add significance stars
        stars = VGroup()
        for i in range(8):
            star = Text("**", font_size=16, color=YELLOW)
            star.next_to(bars[i], UP, buff=0.1)
            stars.add(star)
        self.play(FadeIn(stars), run_time=0.5)

        # Explanation
        expl = Text(
            "Every way of measuring the score\n"
            "correctly predicts recovery.",
            font_size=20, color=WHITE, font="Sans"
        )
        expl.to_edge(DOWN, buff=0.3)
        self.play(Write(expl), run_time=1.5)
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])

    # ─── SCENE 6: The Mystery ───

    def scene_the_mystery(self):
        title = Text("But We Still Don't Know...", font_size=42, color=YELLOW)
        title.to_edge(UP, buff=0.6)
        self.play(Write(title))

        # Show what it's NOT
        nots = VGroup()
        crossed_out = [
            ("Not the number of grains", RED),
            ("Not how fast they move", RED),
            ("Not the shape of the pile", RED),
            ("Not the force on each grain", RED),
        ]
        for i, (text, color) in enumerate(crossed_out):
            t = Text(text, font_size=22, color=color, font="Sans")
            t.shift(DOWN * (i * 0.7 - 0.5) + LEFT * 0.5)
            nots.add(t)

        # Show crossed-out text
        for t in nots:
            self.play(Write(t), run_time=0.6)
            line = Line(
                t.get_left() + LEFT * 0.1,
                t.get_right() + RIGHT * 0.1,
                color=RED, stroke_width=3
            )
            self.play(Create(line), run_time=0.2)

        self.wait(1)

        # The mystery
        mystery = Text(
            "Something else...\n"
            "We're still looking.",
            font_size=30, color=TEAL
        )
        mystery.shift(DOWN * 2.5)
        self.play(FadeIn(mystery, scale=1.2), run_time=1.5)
        self.wait(2)

        # Closing
        closing = Text(
            "Science is about asking questions\n"
            "and not giving up until you find answers.",
            font_size=20, color=GRAY, font="Sans"
        )
        closing.to_edge(DOWN, buff=0.3)
        self.play(Write(closing), run_time=1.5)
        self.wait(3)

        # Fade all
        self.play(*[FadeOut(mob) for mob in self.mobjects])

        # Final card
        final = Text(
            "RD-022: The score is real.\n"
            "What it measures is the next mystery.",
            font_size=24, color=YELLOW, font="Sans"
        )
        self.play(Write(final), run_time=2)
        self.wait(3)
        self.play(FadeOut(final))
