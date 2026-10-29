// GBX-Design-Vorschau: Vorderseite (links) und Rückseite (rechts) nebeneinander, in Druckfarben.
// Öffnen in OpenSCAD -> F5. Mit der Maus drehen, um die Fasen und Vertiefungen zu sehen.
include <gameboy_pi_case.scad>
part = "none";

black  = [0.08, 0.08, 0.1];
purple = [0.55, 0.3, 0.95];

// Vorderseite, von vorne gesehen
translate([-W - 10, 0, 0]) rotate([0, 180, 0]) translate([-W, 0, 0]) mirror_x() {
    color(black) front_shell();
    color("Silver") front_inlay("silver");
    color(purple) front_inlay("purple");
}

// Rückseite, von hinten gesehen
translate([10, 0, -D]) mirror_x() {
    color(black) back_shell();
    color("Silver") back_inlay("silver");
    color(purple) back_inlay("purple");
}
