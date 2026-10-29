// =====================================================================
//  GameboyPi v1.1 – 3D-druckbares Gehäuse im Game-Boy-Color-Stil
//  für die Trägerplatine "GameboyPi" (KiCad) + Raspberry Pi Zero 2 W
//
//  Export einzelner Teile:   openscad -D "part=\"front\"" -o front.stl gameboy_pi_case.scad
//  part = "front" | "back" | "dpad" | "ab" | "startselect" | "knob" | "assembly"
//         "check" + check_idx = n  -> Kollisionsprüfung Bauteil n gegen beide Schalen (leer = OK)
//
//  Koordinaten: Blick von VORNE, x nach rechts, y nach oben,
//  z = 0 ist die Vorderfläche, z wächst Richtung Rückseite.
//  Platinen-Koordinaten (wie in KiCad): Ursprung oben links, y nach unten.
//  Alle Positionen stammen aus electronics/kicad-project/design.py.
// =====================================================================

part = "assembly";
check_idx = 0;

$fn = 64;

// ---------- Design "GBX – Game Boy Emulator" (schwarz / chrom-silber / lila) ----------
include <logo/gbx_logo.scad>        // aus dem Logo-Bild vektorisiert (logo/trace_logo.py)
use <fonts/Michroma-Regular.ttf>    // breite Technik-Schrift für die Slogans (SIL OFL)
FONT            = "Michroma";
edge_chamfer    = 1.2;    // Fase an Vorder- und Rückkante
inlay_depth     = 0.6;    // Tiefe der Logo-Vertiefung = Dicke der Farb-Einlage (3 Schichten à 0.2)
inlay_clearance = 0.0;    // 0 für Mehrfarbdruck (AMS/MMU); 0.1 für separat gedruckte, eingeklebte Einlagen
min_stroke      = 0.12;   // Schrift um diesen Wert verdicken -> druckbare Linienbreite >= 0.45 mm

// ---------- Hauptmaße ----------
W        = 84;      // Breite außen
H        = 140;     // Höhe außen
D        = 28 + 1.3;  // Gesamtdicke (+1.3 mm für das Touch-Display, siehe lcd_touch)
R        = 6;       // Eckradius
wall     = 2;       // Wandstärke
pcb_w    = 78;      // Platinenbreite
pcb_h    = 134;     // Platinenhöhe
pcb_t    = 1.6;
pcb_off  = (W - pcb_w) / 2;   // Platine sitzt mittig, 1 mm Luft zur Wand

// Display-Stapel (MSP2401/2402 Maßzeichnung): 4.0 Abstand + 1.6 Modulplatine + 2.2 LCD + 0.5 Klebeband
lcd_spacer  = 4.0;                                // gedruckte Hülsen (part="spacers")
lcd_touch   = 1.3;                                // resistive Touch-Folie (LAFVIN/MSP2402); 0 für MSP2401
lcd_stack   = lcd_spacer + 1.6 + 2.2 + 0.5 + lcd_touch;
lcd_gap     = 0.5;                                // Luft zwischen Glas und Frontwand (Moosgummi)
z_pcb_front = wall + lcd_gap + lcd_stack;         // = 10.8: Vorderfläche -> Platinen-Oberseite
z_split     = z_pcb_front + pcb_t;                // Trennebene Vorder-/Rückschale
tol         = 0.25;                               // Spiel für bewegliche Teile

// Platinen-Koordinate -> Gehäuse-Koordinate
function P(x, y) = [pcb_off + x, H - pcb_off - y];

// ---------- Bauteil-Positionen (aus design.py) ----------
holes   = [[4, 4], [74, 4], [4, 130], [74, 130]];
dpad_c  = [19, 86];
btn_a   = [64, 80];
btn_b   = [51, 87];
btn_sel = [32, 108];
btn_sta = [46, 108];
led     = [12.5, 56];
spk_c   = [62, 120];
pwr_sw  = [60, 0];          // Schiebeschalter an der Oberkante
jack_x  = 34;               // 3.5-mm-Klinke (Unterkante, vorne bestückt)
vol_y   = 57.5;             // Achse Lautstärkepoti (linke Seite, hinten bestückt)

// Display MSP2402: Modul 77.18 x 42.72, Glas/Backlight 60.26 x 42.72, sichtbare Fläche 48.96 x 36.72
lcd_org      = [0.4, 8.0];
lcd_mod      = [77.18, 42.72];
lcd_active   = [48.96, 36.72];
lcd_act_c    = [lcd_org[0] + 43.44, lcd_org[1] + 21.36];
lcd_glass    = [lcd_org[0] + 10.41, lcd_org[1], 60.26, 42.72];   // x, y, b, h
lens_size    = [62, 46];                // Vertiefung für 1-mm-Acrylscheibe (optional)
lens_depth   = 1.0;

// Tasten
sw_h      = 5.0;    // Höhe 6x6-Taster inkl. Stößel (6x6x5 mm)
btn_proud = 1.6;    // wie weit die Tasten vorne herausstehen
flange_t  = 1.2;
ab_d      = 10;
dpad_arm  = 8.5;
dpad_len  = 25;
ss_len    = 10;     // Start/Select Pille
ss_w      = 4;

// Rückseite: PowerBoost 1000C auf 2.5-mm-Stiftleiste (Bauteilseite zur Rückwand)
pb_z_top  = z_split + 2.5 + 1.6;              // Oberseite PowerBoost-Platine
usb_x     = 18.93;                            // Micro-USB (Laden) an der Unterkante
usb_z     = pb_z_top + 1.4;
pb_leds   = [8.6, 126.0];                     // CHRG (gelb) + DONE (grün), Lichtleiter
pb_holes  = [[10.04, 131.46], [27.82, 131.46]];
// Pi Zero kopfüber auf 8.5 mm Buchsenleiste + 2.5 mm Stiftleiste
z_pi      = z_split + 8.5 + 2.5;
sd_slot_y = 18.8;   // Platinen-y der SD-Karte (rechte Seitenwand)
sd_z      = z_pi - 0.8;
ports     = [[59.1, 13.5], [30.1, 10.5]];   // Mini-HDMI, Micro-USB (Daten): Platinen-x, Breite
port_z    = [z_pi - 4.2, z_pi + 0.6];
battery   = [12.5, 36.5, 53, 35];           // LiPo 103450 inkl. Schutzplatine (bis 52 x 34 x 10 mm): x, y, b, h
post_d    = 5.5;                            // Schraubpfosten der Rückschale

// ---------------------------------------------------------------------
module rbox(w, h, d, r) {
    linear_extrude(d) offset(r) offset(-r) square([w, h]);
}
module rrect2d(w, h, r) { offset(r) offset(-r) square([w, h]); }
module rrect2d_c(s, r) { translate(-s/2) rrect2d(s[0], s[1], r); }

// Gehäusekörper mit Fase an der Unterkante (cb) und/oder Oberkante (ct)
module shell_body(z0, z1, cb = 0, ct = 0) {
    module slab(z, inset) translate([inset, inset, z]) rbox(W - 2*inset, H - 2*inset, 0.01, R - inset);
    hull() {
        slab(z0, cb);
        slab(z0 + cb, 0);
        slab(z1 - ct - 0.01, 0);
        slab(z1 - 0.01, ct);
    }
}

// ---------- Logos (2D, Gehäusekoordinaten) ----------
// Vorderseite: GBX unter dem Display + lila Akzentlinie (wie im Logo-Bild)
front_logo_c = [39, 65.5];     // Platinenkoordinaten
front_logo_w = 34;
back_logo_c  = [39, 80];
back_logo_w  = 56;

module logo_scaled(w) scale(w / 100) children();
module gb_2d(c, w)   translate(P(c[0], c[1])) logo_scaled(w) gbx_gb();
module x_2d(c, w)    translate(P(c[0], c[1])) logo_scaled(w) gbx_x();
module accent_2d(c, w, dy) translate(P(c[0], c[1] + dy)) hull() {   // Linie mit runden Enden, 0.9 mm
    translate([-w/2 + 0.45, 0]) circle(d = 0.9, $fn = 24);
    translate([ w/2 - 0.45, 0]) circle(d = 0.9, $fn = 24);
}
module tagline_2d(s, c, w, dy)
    translate(P(c[0], c[1] + dy)) offset(min_stroke) resize([w, 0], auto = true)
        text(s, size = 3, font = FONT, halign = "center", valign = "center");

// Silber- bzw. Lila-Anteile je Seite (Rückseite gespiegelt, damit sie von hinten lesbar ist)
module front_silver_2d() gb_2d(front_logo_c, front_logo_w);
module front_purple_2d() {
    x_2d(front_logo_c, front_logo_w);
    accent_2d(front_logo_c, 24, front_logo_w / 4.061 / 2 + 1.6);
}
module back_mirror() translate([W, 0]) mirror([1, 0]) children();
module back_silver_2d() back_mirror() {
    gb_2d(back_logo_c, back_logo_w);
    tagline_2d("GAME BOY EMULATOR", back_logo_c, 58, 11.5);
    tagline_2d("PAST MEETS PERFORMANCE", back_logo_c, 62, 21.0);
}
module back_purple_2d() back_mirror() {
    x_2d(back_logo_c, back_logo_w);
    accent_2d(back_logo_c, 30, 16.2);
}

// Einlagen (3D) im Koordinatensystem der jeweiligen Schale
module front_inlay(which) translate([0, 0, 0]) linear_extrude(inlay_depth)
    offset(-inlay_clearance) if (which == "silver") front_silver_2d(); else front_purple_2d();
module back_inlay(which) translate([0, 0, D - inlay_depth]) linear_extrude(inlay_depth)
    offset(-inlay_clearance) if (which == "silver") back_silver_2d(); else back_purple_2d();

module cavity(z0, z1) {
    translate([wall, wall, z0]) rbox(W - 2*wall, H - 2*wall, z1 - z0, R - wall);
}

// Rahmen (Führung) um eine 2D-Form, auf der Innenseite der Frontwand
module guide(h, clearance, t = 1.2) {
    translate([0, 0, wall - 0.01]) linear_extrude(h) difference() {
        offset(clearance + t) children();
        offset(clearance) children();
    }
}

module dpad_2d() {
    union() {
        rrect2d_c([dpad_len, dpad_arm], 1.2);
        rrect2d_c([dpad_arm, dpad_len], 1.2);
    }
}

module pill_2d(l, w) {
    hull() {
        translate([-(l - w)/2, 0]) circle(d = w);
        translate([ (l - w)/2, 0]) circle(d = w);
    }
}

// Rechteck in Platinenkoordinaten (x, y, b, h) als 2D-Fläche in Gehäusekoordinaten
module pcb_rect2d(r) { translate([pcb_off + r[0], H - pcb_off - r[1] - r[3]]) square([r[2], r[3]]); }

// ---------------------- Vorderschale ----------------------
module front_shell() {
    difference() {
        union() {
            difference() {
                shell_body(0, z_split, cb = edge_chamfer);
                cavity(wall, z_split + 1);
            }
            // Schraubdome für die Platine
            for (h = holes) translate([each P(h[0], h[1]), wall - 0.01])
                cylinder(d = 6, h = z_pcb_front - wall);
            // Lautsprecher-Halter (20 mm)
            translate([each P(spk_c[0], spk_c[1]), wall - 0.01])
                difference() { cylinder(d = 23, h = 3.5); cylinder(d = 20.6, h = 10); }
            // Display-Halter: Rahmen um das Glas (zentriert das Modul, 1.5 mm hoch)
            guide(1.5, 0.3) pcb_rect2d(lcd_glass);
            // Führungen gegen Verdrehen: D-Pad und Start/Select
            translate(P(dpad_c[0], dpad_c[1])) guide(2.0, 1.5 + tol) dpad_2d();
            for (b = [btn_sel, btn_sta]) translate(P(b[0], b[1])) guide(2.0, 1.5 + tol) pill_2d(ss_len, ss_w);
        }
        // Schraublöcher (M2.5 selbstschneidend)
        for (h = holes) translate([each P(h[0], h[1]), wall + 1]) cylinder(d = 2.2, h = 20);

        // Display-Fenster + Linsen-Vertiefung
        translate([each P(lcd_act_c[0], lcd_act_c[1]), -1])
            linear_extrude(wall + 2) offset(0.5) square(lcd_active, center = true);
        translate([each P(lcd_act_c[0], lcd_act_c[1]), -0.01])
            linear_extrude(lens_depth) rrect2d_c(lens_size, 3);
        // angefaste Fensterkante (wie die abgeschrägten Chrom-Buchstaben des Logos)
        translate(P(lcd_act_c[0], lcd_act_c[1])) hull() {
            translate([0, 0, lens_depth - 0.01]) linear_extrude(0.01) offset(0.5 + 0.8) square(lcd_active, center = true);
            translate([0, 0, lens_depth + 0.8]) linear_extrude(0.01) offset(0.5) square(lcd_active, center = true);
        }
        // GBX-Logo + Akzentlinie: Vertiefung für die Farb-Einlagen
        translate([0, 0, -0.01]) linear_extrude(inlay_depth + 0.01) { front_silver_2d(); front_purple_2d(); }

        // D-Pad Kreuz, A / B, Start / Select
        translate([each P(dpad_c[0], dpad_c[1]), -1])
            linear_extrude(wall + 2) offset(tol) dpad_2d();
        for (b = [btn_a, btn_b]) translate([each P(b[0], b[1]), -1])
            cylinder(d = ab_d + 2*tol, h = wall + 2);
        for (b = [btn_sel, btn_sta]) translate([each P(b[0], b[1]), -1])
            linear_extrude(wall + 2) offset(tol) pill_2d(ss_len, ss_w);
        // Power-LED
        translate([each P(led[0], led[1]), -1]) cylinder(d = 3.2, h = wall + 2);
        // Lautsprecher-Gitter
        translate(P(spk_c[0], spk_c[1]))
            for (i = [-2:2], j = [-2:2])
                if (i*i + j*j <= 5)
                    translate([i*3.4, j*3.4, -1]) cylinder(d = 1.8, h = wall + 2, $fn = 16);
        // Schlitz Ein/Aus-Schalter (Oberkante)
        translate([P(pwr_sw[0], 0)[0] - 6, H - wall - 1, z_pcb_front - 4.5])
            cube([12, wall + 2, 10]);
        // Kopfhörerbuchse (Unterkante), zur Trennebene offen
        translate([P(jack_x, 0)[0] - 3.75, -1, z_pcb_front - 6.5]) cube([7.5, wall + 2, 10]);
        // Beschriftungs-Prägungen
        translate([each P(led[0] + 3.5, led[1] + 1.1), -0.01])
            linear_extrude(0.4) offset(min_stroke) text("POWER", size = 2.0, font = FONT);
    }
}

// ---------------------- Rückschale ----------------------
module back_shell() {
    difference() {
        union() {
            difference() {
                shell_body(z_split, D, ct = edge_chamfer);
                cavity(z_split - 1, D - wall);
            }
            // Pfosten: drücken die Platine gegen die Dome der Vorderschale
            // Ø5.5: die abgerundete Pi-Ecke hat zum oberen Pfosten nur ~0.4 mm Luft
            for (h = holes) translate([each P(h[0], h[1]), z_split])
                cylinder(d = post_d, h = D - wall - z_split + 0.01);
            // Akku-Halter: Rahmen 4 mm hoch auf dem Boden, Lücke für das Kabel unten links
            translate([0, 0, D - wall - 4]) linear_extrude(4.01) difference() {
                offset(0.5 + 1.2) pcb_rect2d(battery);
                offset(0.5) pcb_rect2d(battery);
                translate(P(battery[0] + 4, battery[1] + battery[3] + 3)) square([8, 6]);
            }
            // PowerBoost-Niederhalter (Stifte in die Montagelöcher)
            for (h = pb_holes) translate([each P(h[0], h[1]), pb_z_top + 0.3]) {
                cylinder(d = 4.5, h = D - wall - pb_z_top);
                translate([0, 0, -1.5]) cylinder(d = 2.0, h = 1.6);
            }
            // Lichtleiter-Rohr über den Lade-LEDs
            translate([each P(pb_leds[0], pb_leds[1]), pb_z_top + 1.8])
                linear_extrude(D - wall - pb_z_top - 1.8 + 0.01) offset(0.8) rrect2d_c([3.2, 6.8], 1.5);
        }
        // Durchgangsloch + Senkung für M2.5 x 20 Schrauben
        for (h = holes) translate(P(h[0], h[1])) {
            translate([0, 0, z_split - 1]) cylinder(d = 2.9, h = D);
            translate([0, 0, D - 3]) cylinder(d = 5.2, h = 4);
        }
        // Micro-USB (Laden, PowerBoost) an der Unterkante
        translate([P(usb_x, 0)[0], -1, usb_z]) rotate([-90, 0, 0]) linear_extrude(wall + 2)
            offset(1.2) offset(-1.2) square([12, 7.5], center = true);
        // Lichtleiter-Öffnung (Lade-LEDs gelb/grün)
        translate([each P(pb_leds[0], pb_leds[1]), pb_z_top + 1.7])
            linear_extrude(D) rrect2d_c([3.2, 6.8], 1.5);
        // Lautstärkeknopf (linke Seite), zur Trennebene offen
        translate([-1, P(0, vol_y)[1] - 4.25, z_split - 1]) cube([wall + 2, 8.5, 11]);
        // microSD-Zugang (rechte Seitenwand)
        translate([W - wall - 1, P(0, sd_slot_y)[1] - 7, sd_z - 1.6]) cube([wall + 2, 14, 3.2]);
        // Mini-HDMI und Micro-USB (Daten) des Pi (Oberkante)
        for (p = ports) translate([P(p[0], 0)[0] - p[1]/2, H - wall - 1, port_z[0]])
            cube([p[1], wall + 2, port_z[1] - port_z[0]]);
        // Lüftungsschlitze über dem Pi
        for (i = [0:7]) translate([P(14 + i*7, 0)[0], P(0, 30)[1] - 9, D - wall - 1])
            linear_extrude(wall + 2) rrect2d(2.2, 18, 1.0);
        // Beschriftung Ladeanzeige
        translate([each P(pb_leds[0] + 3.5, pb_leds[1] + 1), D - 0.4])
            linear_extrude(1) mirror([1, 0, 0]) offset(min_stroke) text("CHG", size = 2.0, font = FONT);
        // GBX-Logo, Slogans und Akzentlinie: Vertiefung für die Farb-Einlagen
        translate([0, 0, D - inlay_depth]) linear_extrude(inlay_depth + 0.01) { back_silver_2d(); back_purple_2d(); }
    }
}

// ---------------------- Tasten ----------------------
// Alle Tasten werden mit der Druckfläche nach unten gedruckt:
//   Kappe (ragt durch die Front) -> Flansch (liegt innen an der Front) -> Stößel (drückt auf den Taster)
cap_h   = wall + btn_proud;
stem_h  = z_pcb_front - sw_h - wall - flange_t - 0.15;
pivot_h = z_pcb_front - wall - flange_t - 0.3;       // D-Pad Kipp-Noppe bis zur Platine

// children: 0 = Kappe (2D), 1 = Flansch (2D), 2 = Stößel (3D)
module button_stack() {
    linear_extrude(cap_h) children(0);
    translate([0, 0, cap_h - 0.01]) linear_extrude(flange_t) children(1);
    translate([0, 0, cap_h + flange_t - 0.02]) children(2);
}

module ab_button() {
    button_stack() {
        circle(d = ab_d);
        circle(d = ab_d + 3);
        cylinder(d = 5, h = stem_h);
    }
}

module dpad() {
    sw_off = 7.5;   // Taster-Abstand vom D-Pad-Mittelpunkt
    button_stack() {
        dpad_2d();
        offset(1.5) dpad_2d();
        union() {
            for (a = [0:90:270]) rotate(a) translate([sw_off, 0, 0]) cylinder(d = 4, h = stem_h);
            cylinder(d = 3, h = pivot_h);
        }
    }
}

module ss_button() {
    button_stack() {
        pill_2d(ss_len, ss_w);
        offset(1.5) pill_2d(ss_len, ss_w);
        linear_extrude(stem_h) pill_2d(6, 2.6);
    }
}

// Lautstärkeknopf für Bourns PTV09A-2020F-A103 (6-mm-Achse mit Abflachung, auf ~4 mm außerhalb kürzen)
knob_d = 12; knob_h = 6; shaft_d = 6.1; shaft_flat = 4.6;
module knob() {
    difference() {
        union() {
            cylinder(d = knob_d, h = knob_h);
            for (a = [0:15:359]) rotate(a) translate([knob_d/2, 0, 0]) cylinder(d = 1.2, h = knob_h, $fn = 8);
        }
        translate([0, 0, 1.2]) intersection() {
            cylinder(d = shaft_d, h = knob_h);
            translate([-shaft_d/2, -shaft_d/2 + (shaft_d - shaft_flat), 0]) cube([shaft_d, shaft_flat, knob_h]);
        }
    }
}

// ---------------------- Bauteil-Hüllkörper für die Kollisionsprüfung ----------------------
// Jeder Eintrag: Name, [x, y, b, h] in Platinenkoordinaten, [z0, z1]
// Bewusst nach außen ragende Teile (Schalterhebel, Klinkenöffnung, Poti-Achse, Ports) sind nicht enthalten.
comps = [
    ["Platine",            [0, 0, 78, 134],              [z_pcb_front, z_split], 3],
    ["Display-Modul",      [0.4, 8, 77.18, 42.72],       [z_pcb_front - lcd_spacer - 1.6, z_pcb_front - lcd_spacer]],
    ["Display-Glas",       [10.81, 8, 60.26, 42.72],     [wall + lcd_gap, z_pcb_front - lcd_spacer - 1.6]],
    ["Display-Stiftleiste",[0.4 + 0.73, 8 + 3.5, 2.54, 35.6], [z_pcb_front - lcd_spacer, z_pcb_front]],
    ["Taster UP",          [16, 75.5, 6, 6],             [z_pcb_front - 3.5, z_pcb_front]],
    ["Taster A",           [61, 77, 6, 6],               [z_pcb_front - 3.5, z_pcb_front]],
    ["Taster START",       [43, 105, 6, 6],              [z_pcb_front - 3.5, z_pcb_front]],
    ["Schalter-Koerper",   [55.7, 0, 8.6, 4.6],          [z_pcb_front - 3.6, z_pcb_front]],
    ["Klinke-Koerper",     [28, 121, 12, 13],            [z_pcb_front - 5.2, z_pcb_front]],
    ["Audio-Elkos",        [20.6, 118.85, 6.3, 13.2],    [z_pcb_front - 6.0, z_pcb_front]],   // 2x ECE-A1AKS101 Ø6.3x6
    ["Lautsprecher",       [55, 113, 14, 14],            [wall, wall + 4]],   // Quadrat innerhalb Ø20
    ["Pi Zero + Buchse",   [6.5, 3.77, 65, 30],          [z_split, z_pi + 1.6], 3],
    ["Akku 103450",        [12.5, 36.5, 53, 35],         [z_split + 1.5, z_split + 11.5]],
    ["PowerBoost-Platine", [7.5, 97.94, 22.86, 31.5],    [z_split + 2.5, pb_z_top]],   // ohne Lochstreifen
    ["PowerBoost-Bauteile",[7.5, 97.94, 22.86, 23.0],    [pb_z_top, pb_z_top + 1.5]],  // bis vor die LEDs
    ["PowerBoost-USB",     [14.9, 128.5, 8.0, 5.5],      [pb_z_top, pb_z_top + 3.0]],
    ["PowerBoost-JST",     [23.8, 120.8, 6.0, 5.0],      [pb_z_top, pb_z_top + 4.6]],
    ["PAM8302",            [60.38, 74.92, 15.24, 24.13], [z_split, z_split + 2.5 + 1.6 + 8.5]],
    ["ADS1115",            [30, 72, 17.78, 25.4],        [z_split, z_split + 2.5 + 1.6 + 1.5]],
    ["Elko 470uF",         [62.85, 122.85, 6.3, 6.3],    [z_split, z_split + 12.5]],
    ["Poti PTV09A-2",      [0.3, 52.6, 6.8, 9.8],        [z_split, z_split + 11.5]],
];

// optional c[3]: Eckradius (Platine, Pi Zero)
module comp_body(c) {
    r = len(c) > 3 ? c[3] : 0;
    translate([0, 0, c[2][0]]) linear_extrude(c[2][1] - c[2][0])
        if (r > 0) offset(r) offset(-r) pcb_rect2d(c[1]); else pcb_rect2d(c[1]);
}

// ---------------------- Auswahl ----------------------
// Die Modellierung erfolgt "von vorne gesehen" mit z nach hinten – das ist ein linkshändiges System.
// mirror_x() spiegelt einmal an x, damit das gedruckte Teil seitenrichtig zur Platine ist.
module mirror_x() { translate([W, 0, 0]) mirror([1, 0, 0]) children(); }

module front_print() mirror_x() children();                                // Vorderseite auf dem Druckbett
module back_print()  translate([0, H, D]) rotate([180, 0, 0]) mirror_x() children();   // Rückseite auf dem Druckbett

if (part == "front") {
    front_print() front_shell();
} else if (part == "back") {
    back_print() back_shell();
// Farb-Einlagen: gleiche Lage wie die zugehörige Schale -> im Slicer "als Teil hinzufügen" und Farbe zuweisen
} else if (part == "front_logo_silver") {
    front_print() front_inlay("silver");
} else if (part == "front_logo_purple") {
    front_print() front_inlay("purple");
} else if (part == "back_logo_silver") {
    back_print() back_inlay("silver");
} else if (part == "back_logo_purple") {
    back_print() back_inlay("purple");
} else if (part == "showcase") {
    // Farbvorschau im GBX-Design (Vorderseite nach unten)
    mirror_x() {
        color([0.08, 0.08, 0.1]) front_shell();
        color("Silver") front_inlay("silver");
        color([0.55, 0.3, 0.95]) front_inlay("purple");
    }
} else if (part == "showcase_back") {
    mirror_x() {
        color([0.08, 0.08, 0.1]) back_shell();
        color("Silver") back_inlay("silver");
        color([0.55, 0.3, 0.95]) back_inlay("purple");
    }
} else if (part == "none") {
    // nichts ausgeben (für Dateien, die dieses Modell einbinden, z. B. design_preview.scad)
} else if (part == "dpad") {
    dpad();
} else if (part == "ab") {
    translate([-8, 0, 0]) ab_button();
    translate([ 8, 0, 0]) ab_button();
} else if (part == "startselect") {
    translate([0, -5, 0]) ss_button();
    translate([0,  5, 0]) ss_button();
} else if (part == "spacers") {
    // 2 Abstandshülsen Display <-> Platine (M3 x 14 Schraube + Mutter)
    for (x = [-5, 5]) translate([x, 0, 0]) difference() {
        cylinder(d = 6, h = lcd_spacer);
        translate([0, 0, -1]) cylinder(d = 3.4, h = lcd_spacer + 2);
    }
} else if (part == "knob") {
    knob();
} else if (part == "check") {
    // leer = keine Kollision; Toleranz 0.05 mm gegen Berührungsflächen
    echo(str("CHECK ", comps[check_idx][0]));
    intersection() {
        union() { front_shell(); back_shell(); }
        translate([0, 0, 0]) resize_inset(comps[check_idx]);
    }
} else {
    // Explosionsansicht (Vorderseite zeigt nach unten, -z)
    mirror_x() {
        color([0.08, 0.08, 0.1]) front_shell();
        color("Silver") front_inlay("silver");
        color([0.55, 0.3, 0.95]) front_inlay("purple");
        color([0.08, 0.08, 0.1]) translate([0, 0, 25]) back_shell();
        color("ForestGreen") translate([pcb_off, pcb_off, z_pcb_front + 12])
            linear_extrude(pcb_t) rrect2d(pcb_w, pcb_h, 3);
    }
}

// Hüllkörper minimal verkleinert, damit reine Flächenberührung nicht als Kollision zählt
module resize_inset(c) {
    e = 0.05;
    comp_body([c[0], [c[1][0] + e, c[1][1] + e, c[1][2] - 2*e, c[1][3] - 2*e], [c[2][0] + e, c[2][1] - e], len(c) > 3 ? c[3] : 0]);
}
