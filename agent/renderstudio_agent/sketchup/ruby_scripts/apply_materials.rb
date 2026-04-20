# apply_materials.rb — Sprint 3
# 讀 RS_ARGS_JSON: { skp_in, style: StyleSchema }
# 把 StyleSchema 的材質套到 model

require 'json'
require 'sketchup'

def rs_log(msg)
  STDERR.puts "[RS] #{msg}"
  STDERR.flush
end

begin
  args     = JSON.parse(ENV.fetch("RS_ARGS_JSON", "{}"))
  skp_in   = args["skp_in"]
  style    = args["style"] || {}
  out_path = ENV.fetch("RS_OUTPUT", skp_in)

  model = Sketchup.active_model
  if skp_in && File.exist?(skp_in)
    model.load(skp_in) rescue nil
  end

  materials = model.materials

  # 地板
  floor_mat   = materials.add("RS_Floor")
  floor_color = style.dig("floor", "color") || "#C9A97A"
  floor_mat.color = Sketchup::Color.new(floor_color)

  # 牆面
  wall_mat   = materials.add("RS_Wall")
  wall_color = style.dig("wall", "color") || "#F5F1E8"
  wall_mat.color = Sketchup::Color.new(wall_color)

  # 天花板
  ceil_mat   = materials.add("RS_Ceiling")
  ceil_color = style.dig("ceiling", "color") || "#FFFFFF"
  ceil_mat.color = Sketchup::Color.new(ceil_color)

  # 套用到對應 group（依 group name 判斷）
  model.active_entities.each do |ent|
    next unless ent.is_a?(Sketchup::Group)
    ent.material = wall_mat  # 預設全部套牆材質
  end

  model.save(out_path)
  rs_log "materials applied, saved to #{out_path}"

rescue => e
  rs_log "FATAL: #{e}"
  exit 1
ensure
  Sketchup.quit
end
