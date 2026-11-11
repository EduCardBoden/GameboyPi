// PreToolUse (Edit|Write|NotebookEdit): blocks hand edits of generated GameboyPi files.
// They are rebuilt by electronics/kicad-project/build.ps1 and mechanical/cad-source/build.ps1.
let raw = "";
process.stdin.on("data", (c) => (raw += c)).on("end", () => {
  let p = "";
  try { p = (JSON.parse(raw).tool_input || {}).file_path || ""; } catch { process.exit(0); }
  const f = p.split(String.fromCharCode(92)).join("/");
  const rules = [
    [/\.kicad_(pcb|sch)$/i, "design.py / make_sch.py / make_pcb.py / route.py, then the pcb-build skill"],
    [/\/electronics\/(gerber|assembly|schematics)\//i, "the PCB generators, then the pcb-build skill"],
    [/\/mechanical\/(stl|previews)\//i, "gameboy_pi_case.scad, then the case-build skill"],
    [/\/bestellung\/.*\.(stl|zip|png)$/i, "the build scripts (they copy into bestellung/)"],
    [/\/build\/[^/]+$/i, "the build scripts (build/ is output)"],
  ];
  for (const [re, fix] of rules) {
    if (re.test(f)) {
      process.stderr.write(`Blocked: ${p} is generated. Change ${fix} instead (see GameboyPi/CLAUDE.md).`);
      process.exit(2);
    }
  }
  process.exit(0);
});
