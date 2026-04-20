# generate_model.rb — Sprint 0 PoC
# 讀 ENV["RS_ARGS_JSON"] 拿牆體/門窗/房間資料，產出 .skp 到 ENV["RS_OUTPUT"]
# 執行方式：SketchUp -RubyStartup generate_model.rb

require 'json'
require 'sketchup'

def rs_log(msg)
  STDERR.puts "[RS] #{msg}"
  STDERR.flush
end

begin
  args     = JSON.parse(ENV.fetch("RS_ARGS_JSON", "{}"))
  out_path = ENV.fetch("RS_OUTPUT", "/tmp/output.skp")

  model    = Sketchup.active_model
  entities = model.active_entities
  model.start_operation("RenderStudio Generate", true)

  walls          = args["walls"]      || []
  openings_data  = args["openings"]   || []
  ceiling_height = (args["ceiling_height_mm"] || 2700).to_f

  # ── 建牆體（擠出到天花板高度）──────────────────────────────
  wall_group = entities.add_group
  wg_ents    = wall_group.entities

  walls.each do |w|
    x0, y0 = w["x0"].to_f.mm, w["y0"].to_f.mm
    x1, y1 = w["x1"].to_f.mm, w["y1"].to_f.mm
    h       = ceiling_height.mm

    thickness = 150.mm  # 預設牆厚 150mm

    dx = x1 - x0
    dy = y1 - y0
    len = Math.sqrt(dx*dx + dy*dy)
    next if len < 1.mm

    # 建底面矩形 (順時針)
    nx = -dy / len * thickness / 2
    ny =  dx / len * thickness / 2

    pts = [
      Geom::Point3d.new(x0 + nx, y0 + ny, 0),
      Geom::Point3d.new(x1 + nx, y1 + ny, 0),
      Geom::Point3d.new(x1 - nx, y1 - ny, 0),
      Geom::Point3d.new(x0 - nx, y0 - ny, 0),
    ]

    face = wg_ents.add_face(pts)
    face.pushpull(h) if face
  rescue => e
    rs_log "wall error: #{e}"
  end

  # ── 建地板 ─────────────────────────────────────────────────
  bbox = args["bbox"]
  if bbox && bbox["min_x"]
    x0 = bbox["min_x"].to_f.mm - 200.mm
    y0 = bbox["min_y"].to_f.mm - 200.mm
    x1 = bbox["max_x"].to_f.mm + 200.mm
    y1 = bbox["max_y"].to_f.mm + 200.mm
    floor_group  = entities.add_group
    floor_ents   = floor_group.entities
    floor_pts    = [
      Geom::Point3d.new(x0, y0, 0),
      Geom::Point3d.new(x1, y0, 0),
      Geom::Point3d.new(x1, y1, 0),
      Geom::Point3d.new(x0, y1, 0),
    ]
    floor_face = floor_ents.add_face(floor_pts)
    floor_face.reverse! if floor_face && floor_face.normal.z < 0
  end

  model.commit_operation

  # 存檔
  model.save(out_path)
  rs_log "saved to #{out_path}"

rescue => e
  rs_log "FATAL: #{e}\n#{e.backtrace.first(5).join("\n")}"
  model.abort_operation rescue nil
  exit 1
ensure
  Sketchup.quit
end
