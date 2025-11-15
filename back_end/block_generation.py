import numpy as np
import random
from collections import defaultdict
import json # Used for JSON serializable constants

# --- Global Constants ---
# Use JSON serializable dict for constants
CONSTANTS = {
    'MODULE_SIZE': {'x': 2.75, 'y': 2.75, 'z': 3.0},
    'BLOCK_SIZES': {
        'Comfort': (2, 2, 1),
        'Transparent': (1, 2, 1),
        'Opaque': (2, 2, 1)
    },
    'BLOCK_COLORS': {
        'Comfort': '#FFD700', # gold
        'Transparent': '#87CEEB', # skyblue
        'Opaque': '#3CB371' # mediumseagreen
    },
    'GRID_MAX': 5
}
GRID_MAX = CONSTANTS['GRID_MAX']
MODULE_SIZE = CONSTANTS['MODULE_SIZE']
BLOCK_SIZES = CONSTANTS['BLOCK_SIZES']


# --- Analyzer Class (for Parameters, COG, Main Front) ---

class ConfigurationAnalyzer:
    def __init__(self, final_coords):
        self.final_coords = final_coords
        self.max_x = max(x + dx for x, y, z, dx, dy, dz, type in final_coords.values()) if final_coords else 0
        self.max_y = max(y + dy for x, y, z, dx, dy, dz, type in final_coords.values()) if final_coords else 0
        self.max_z = max(z + dz for x, y, z, dx, dy, dz, type in final_coords.values()) if final_coords else 0

    # Topic 2: Parameters
    def calculate_simple_parameters(self):
        W_max = self.max_x * MODULE_SIZE['x']
        L_max = self.max_y * MODULE_SIZE['y']
        H_max = self.max_z * MODULE_SIZE['z']
        total_volume = 0
        for x, y, z, dx, dy, dz, type in self.final_coords.values():
            V_i = dx * dy * dz * MODULE_SIZE['x'] * MODULE_SIZE['y'] * MODULE_SIZE['z']
            total_volume += V_i
        return {
            'W_max': f"{W_max:.2f} m",
            'L_max': f"{L_max:.2f} m",
            'H_max': f"{H_max:.2f} m",
            'Volume_V': f"{total_volume:.2f} m³"
        }

    # Topic 5: Centre of Gravity
    def calculate_centre_of_gravity(self):
        total_mass_moment_x, total_mass_moment_y, total_mass_moment_z, total_volume = 0, 0, 0, 0
        for x_mod, y_mod, z_mod, dx_mod, dy_mod, dz_mod, type in self.final_coords.values():
            dx_phys = dx_mod * MODULE_SIZE['x']
            dy_phys = dy_mod * MODULE_SIZE['y']
            dz_phys = dz_mod * MODULE_SIZE['z']
            V_i = dx_phys * dy_phys * dz_phys
            
            # Physical center coordinates
            X_center = ((x_mod - 1) * MODULE_SIZE['x']) + (dx_phys / 2)
            Y_center = ((y_mod - 1) * MODULE_SIZE['y']) + (dy_phys / 2)
            Z_center = ((z_mod - 1) * MODULE_SIZE['z']) + (dz_phys / 2)

            total_mass_moment_x += X_center * V_i
            total_mass_moment_y += Y_center * V_i
            total_mass_moment_z += Z_center * V_i
            total_volume += V_i
        
        if total_volume == 0: return {'X': 0, 'Y': 0, 'Z': 0}
        
        return {
            'X': total_mass_moment_x / total_volume,
            'Y': total_mass_moment_y / total_volume,
            'Z': total_mass_moment_z / total_volume
        }

    # Topic 6: Main Front
    def determine_main_front(self):
        exposed_faces = defaultdict(int) 
        occupied_modules = set()
        for x, y, z, dx, dy, dz, _ in self.final_coords.values():
            for i in range(x, x + dx):
                for j in range(y, y + dy):
                    for k in range(z, z + dz):
                        occupied_modules.add((i, j, k))

        for x, y, z, dx, dy, dz, _ in self.final_coords.values():
            for i in range(x, x + dx):
                for j in range(y, y + dy):
                    for k in range(z, z + dz):
                        if (i + 1, j, k) not in occupied_modules and i + 1 <= GRID_MAX: exposed_faces['X+'] += 1
                        if (i - 1, j, k) not in occupied_modules and i > 1: exposed_faces['X-'] += 1
                        if (i, j + 1, k) not in occupied_modules and j + 1 <= GRID_MAX: exposed_faces['Y+'] += 1
                        if (i, j - 1, k) not in occupied_modules and j > 1: exposed_faces['Y-'] += 1
                        
        facade_areas = {}
        max_area = 0
        face_area = MODULE_SIZE['x'] * MODULE_SIZE['z']

        for direction, modules in exposed_faces.items():
            area = modules * face_area
            facade_areas[direction] = area
            max_area = max(max_area, area)
            
        main_front = "N/A"
        if max_area > 0:
            for direction, area in facade_areas.items():
                if area == max_area:
                    main_front = direction
                    break

        return main_front, {k: f'{v:.2f} m²' for k, v in facade_areas.items()}


# --- Rule Check Logic ---

def check_gravity_on_ground(final_coords):
    comfort_on_ground = 0
    opaque_violation = False
    for _, (x, y, z, dx, dy, dz, type) in final_coords.items():
        if z == 1:
            if type == 'Comfort': comfort_on_ground += 1
        if type == 'Opaque' and z > 1: opaque_violation = True
    return comfort_on_ground >= 2, not opaque_violation

def check_max_stacking_rule_2_4_1(grid_occupancy, final_coords):
    violation_2_4_1 = False
    for x in range(1, GRID_MAX + 1):
        for y in range(1, GRID_MAX + 1):
            occupied_z = [z for z in range(1, GRID_MAX + 1) if grid_occupancy.get((x, y, z)) is not None]
            if len(occupied_z) > 3:
                violation_2_4_1 = True
    return not violation_2_4_1

def check_long_house_rule_2_4_3(final_coords):
    ground_footprint = np.zeros((GRID_MAX + 1, GRID_MAX + 1), dtype=int)
    for _, (x, y, z, dx, dy, dz, _) in final_coords.items():
        if z == 1:
            for i in range(x, x + dx):
                for j in range(y, y + dy):
                    ground_footprint[i, j] = 1

    max_x_run, max_y_run = 0, 0
    for j in range(1, GRID_MAX + 1):
        current_run = 0
        for i in range(1, GRID_MAX + 1):
            current_run = current_run + 1 if ground_footprint[i, j] == 1 else 0
            max_x_run = max(max_x_run, current_run)

    for i in range(1, GRID_MAX + 1):
        current_run = 0
        for j in range(1, GRID_MAX + 1):
            current_run = current_run + 1 if ground_footprint[i, j] == 1 else 0
            max_y_run = max(max_y_run, current_run)
        
    return (max_x_run <= 4) and (max_y_run <= 4)

def check_connectivity(final_coords):
    if len(final_coords) <= 1: return True
    start_id = min(final_coords.keys())
    connected_set = {start_id}
    queue = [start_id]
    
    while queue:
        current_block_id = queue.pop(0)
        cx, cy, cz, cdx, cdy, cdz, ctype = final_coords[current_block_id]
        
        for other_id, (ox, oy, oz, odx, ody, odz, otype) in final_coords.items():
            if other_id not in connected_set:
                x_overlap = (cx < ox + odx and cx + cdx > ox)
                y_overlap = (cy < oy + ody and cy + cdy > oy)
                z_overlap = (cz < oz + odz and cz + cdz > oz)
                
                is_adjacent = False
                if x_overlap and y_overlap and (cz + cdz == oz or oz + odz == cz): is_adjacent = True
                elif x_overlap and z_overlap and (cy + cdy == oy or oy + ody == cy): is_adjacent = True
                elif y_overlap and z_overlap and (cx + cdx == ox or ox + odx == cx): is_adjacent = True
                    
                if is_adjacent:
                    connected_set.add(other_id)
                    queue.append(other_id)
                    
    return len(connected_set) == len(final_coords)


def perform_detailed_rule_check(final_coords, required_counts, attempt_num):
    log = []
    is_valid = True
    
    # Grid Occupancy for Z-Stacking Check
    grid_occupancy = {}
    for block_id, (x, y, z, dx, dy, dz, type) in final_coords.items():
        for i in range(x, x + dx):
            for j in range(y, y + dy):
                for k in range(z, z + dz):
                    grid_occupancy[(i, j, k)] = block_id

    # 2.1: All required blocks placed (implicit in generation)
    log.append({"rule": "2.1 Required Block Count", "status": "PASS", "message": f"All {sum(required_counts.values())} blocks placed."})

    # 2.2 / 5.1.1: Gravitational Rule & Opaque on Ground Check
    rule_2_2_passed, rule_5_1_1_passed = check_gravity_on_ground(final_coords)
    log.append({"rule": "2.2 Min Comfort on Ground (>=2)", "status": "PASS" if rule_2_2_passed else "FAIL", "message": f"Status: {rule_2_2_passed}"})
    log.append({"rule": "5.1.1 Opaque Only on Ground (Z=1)", "status": "PASS" if rule_5_1_1_passed else "FAIL", "message": f"Status: {rule_5_1_1_passed}"})
    if not rule_2_2_passed or not rule_5_1_1_passed: is_valid = False

    # 2.3: Compactness (Connectivity)
    is_connected = check_connectivity(final_coords)
    log.append({"rule": "2.3 Compactness (Connectivity)", "status": "PASS" if is_connected else "FAIL", "message": f"Status: {is_connected}"})
    if not is_connected: is_valid = False
    
    # 2.4.1: Stacking Rule Fix (Max 3 stacked zones)
    rule_2_4_1_passed = check_max_stacking_rule_2_4_1(grid_occupancy, final_coords)
    log.append({"rule": "2.4.1 Max 3 Stacked Zones", "status": "PASS" if rule_2_4_1_passed else "FAIL", "message": f"Status: {rule_2_4_1_passed}"})
    if not rule_2_4_1_passed: is_valid = False
            
    # 2.4.3: Long House Rule (Max 4 modules in a straight line)
    rule_2_4_3_passed = check_long_house_rule_2_4_3(final_coords)
    log.append({"rule": "2.4.3 No Long House on Ground (Max 4 modules)", "status": "PASS" if rule_2_4_3_passed else "FAIL", "message": f"Status: {rule_2_4_3_passed}"})
    if not rule_2_4_3_passed: is_valid = False

    log.append({"rule": "Attempt Status", "status": "PASS" if is_valid else "FAIL", "message": f"Attempt {attempt_num} Final Status: {'VALID' if is_valid else 'INVALID'}"})
    
    return is_valid, log


# --- Backtrack Generation Core Function ---

def try_generate_configuration(required_counts, max_attempts=500):
    final_coords = {}
    current_id = 1
    
    block_types = []
    block_types.extend(['Comfort'] * required_counts['comfort'])
    block_types.extend(['Transparent'] * required_counts['transparent'])
    block_types.extend(['Opaque'] * required_counts['opaque'])
    random.shuffle(block_types)
    
    for block_type in block_types:
        dx, dy, dz = BLOCK_SIZES[block_type]
        placed = False
        attempts = 0
        
        while not placed and attempts < max_attempts:
            attempts += 1
            
            # 1. Select random position (1-based index) - Enforce boundary
            nx = random.randint(1, GRID_MAX - dx + 1)
            ny = random.randint(1, GRID_MAX - dy + 1)
            nz = random.randint(1, GRID_MAX - dz + 1)
            
            # 2. Collision check
            is_colliding = False
            for ox, oy, oz, odx, ody, odz, otype in final_coords.values():
                if (nx < ox + odx and nx + dx > ox and
                    ny < oy + ody and ny + dy > oy and
                    nz < oz + odz and nz + dz > oz):
                    is_colliding = True
                    break
            
            if not is_colliding:
                # 3. Connectivity check
                if current_id > 1:
                    is_connected_to_existing = False
                    for ox, oy, oz, odx, ody, odz, otype in final_coords.values():
                        # Check adjacency (shared face)
                        x_overlap = (nx < ox + odx and nx + dx > ox)
                        y_overlap = (ny < oy + ody and ny + dy > oy)
                        z_overlap = (nz < oz + odz and nz + dz > oz)
                        
                        is_adjacent = False
                        if x_overlap and y_overlap and (nz + dz == oz or oz + odz == nz): is_adjacent = True
                        elif x_overlap and z_overlap and (ny + dy == oy or oy + ody == ny): is_adjacent = True
                        elif y_overlap and z_overlap and (nx + dx == ox or ox + odx == nx): is_adjacent = True
                            
                        if is_adjacent:
                            is_connected_to_existing = True
                            break
                    
                    if not is_connected_to_existing:
                        continue 
            
            # 4. Placement successful
            final_coords[current_id] = (nx, ny, nz, dx, dy, dz, block_type)
            current_id += 1
            placed = True
        
        if not placed:
            return {}
    
    return final_coords


# --- API Endpoint Function (Topic 3: Backtrack Generation) ---

def generate_configuration_api(comfort_count, transparent_count, opaque_count, max_overall_attempts=1000):
    required_counts = {
        'comfort': comfort_count,
        'transparent': transparent_count,
        'opaque': opaque_count
    }
    
    full_log = []
    attempts = 0
    final_coords = {}
    is_valid_config = False

    while attempts < max_overall_attempts:
        attempts += 1
        
        # 1. Generate a configuration
        current_coords = try_generate_configuration(required_counts)
        
        if not current_coords:
            full_log.append({"rule": "Generation Failure", "status": "FAIL", "message": f"Attempt {attempts} failed: Could not place all blocks while maintaining connectivity and no collision."})
            continue
        
        # 2. Rule Check
        is_valid, rule_log = perform_detailed_rule_check(current_coords, required_counts, attempts)
        full_log.extend(rule_log)
        
        if is_valid:
            is_valid_config = True
            final_coords = current_coords
            break
        else:
            # Add separation for failed attempts in log
            full_log.append({"rule": "Separator", "status": "SEPARATOR", "message": f"--- End of Attempt {attempts} (Invalid) ---"})
            
    
    if is_valid_config:
        analyzer = ConfigurationAnalyzer(final_coords)
        
        # Topic 2: Parameters
        parameters = analyzer.calculate_simple_parameters()
        
        # Topic 5: Centre of Gravity
        cog = analyzer.calculate_centre_of_gravity()
        
        # Topic 6: Main Front
        main_front, facade_areas = analyzer.determine_main_front()
        
        result_coords = []
        for id, (x, y, z, dx, dy, dz, type) in final_coords.items():
            result_coords.append({
                'id': id,
                'type': type,
                # Module coordinates (1-based) and dimensions (modules)
                'x': x, 'y': y, 'z': z, 
                'dx': dx, 'dy': dy, 'dz': dz,
            })
        
        return {
            'success': True,
            'console': f"SUCCESS! Valid configuration found after {attempts} attempts.",
            'coords': result_coords,
            'analysis': {
                'parameters': parameters,
                'cog': cog,
                'main_front': main_front,
                'facade_areas': facade_areas
            },
            'log': full_log
        }
    else:
        return {
            'success': False,
            'console': f"FAILURE! Could not find a valid configuration after {max_overall_attempts} attempts. Check rule log for details.",
            'coords': [],
            'analysis': {},
            'log': full_log
        }

if __name__ == '__main__':
    # Example usage for testing
    result = generate_configuration_api(5, 3, 1, 10)
    print(json.dumps(result, indent=4))