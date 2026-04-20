# place_furniture.rb — Sprint 3
# 讀 RS_ARGS_JSON: { skp_in, rooms, style }
# 依房間類型與 furniture_language 擺放家具 (construction point + text label)

require 'json'
require 'sketchup'

def rs_log(msg)
  STDERR.puts "[RS] #{msg}"
  STDERR.flush
end

FURNITURE_CONFIG = {
  "nordic-minimal" => {
    "living_room" => ["sofa", "coffee_table", "floor_lamp"],
    "bedroom"     => ["bed", "wardrobe"],
    "kitchen"     => ["dining_table", "chair"],
    "bathroom"    => ["vanity"],
  },
  "industrial" => {
    "living_room" => ["sofa", "coffee_table"],
    "bedroom"     => ["bed"],
    "kitchen"     => ["dining_table"],
    "bathroom"    => ["vanity"],
  },
}.freeze

FALLBACK_FURNITURE = {
  "living_room" => ["sofa", "coffee_table"],
  "bedroom"     => ["bed"],
  "kitchen"     => ["dining_table", "chair"],
  "bathroom"    => ["vanity"],
}.freeze

begin
  args_json = ENV.fetch("RS_ARGS_JSON", "{}")
  args      = JSON.parse(args_json)

  skp_in   = args["skp_in"]
  rooms    = args["rooms"]  || []
  style    = args["style"]  || {}
  lang     = style["furniture_language"] || ""
  out_path = ENV.fetch("RS_OUTPUT", skp_in)

  raise ArgumentError, "skp_in is required" if skp_in.nil? || skp_in.empty?

  rs_log "Starting place_furniture: skp_in=#{skp_in}, rooms=#{rooms.size}, language=#{lang}"

  model = Sketchup.active_model
  if File.exist?(skp_in)
    model.load(skp_in)
    rs_log "Loaded model: #{skp_in}"
  else
    rs_log "WARN: skp_in not found (#{skp_in}), using active model"
  end

  entities = model.active_entities
  scheme   = FURNITURE_CONFIG[lang] || FALLBACK_FURNITURE

  rooms.each do |room|
    room_type  = room["room_type"] || "living_room"
    centroid_x = (room["centroid_x"] || 0).to_f
    centroid_y = (room["centroid_y"] || 0).to_f

    furniture_list = scheme[room_type] || FALLBACK_FURNITURE[room_type] || ["sofa"]

    cx = centroid_x.mm
    cy = centroid_y.mm
    pt = Geom::Point3d.new(cx, cy, 0)

    # 在重心放 construction point（暫代家具位置，Sprint 4 將換成真實 component）
    entities.add_cpoint(pt)

    # 加 text label 顯示家具清單
    label = "[#{room_type}] #{furniture_list.join(', ')}"
    text_pt = Geom::Point3d.new(cx, cy, 0)
    entities.add_text(label, text_pt)

    rs_log "Room #{room_type}: centroid=(#{centroid_x}, #{centroid_y}), furniture=#{furniture_list.inspect}"
  end

  model.save(out_path)
  rs_log "Furniture placed and model saved to #{out_path}"

rescue ArgumentError => e
  rs_log "ARG ERROR: #{e}"
  exit 1
rescue => e
  rs_log "FATAL: #{e.class}: #{e.message}"
  rs_log e.backtrace.first(5).join("\n") rescue nil
  exit 1
ensure
  Sketchup.quit
end
