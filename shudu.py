import random
import time
from copy import deepcopy

import streamlit as st


DIGITS = list(range(1, 10))

DIFFICULTY_CLUES = {
    "简单": 42,
    "中等": 36,
    "困难": 30,
    "专家": 26,
}


# =========================
# 数独生成
# =========================

def pattern(r, c):
    return (3 * (r % 3) + r // 3 + c) % 9


def shuffled(seq):
    seq = list(seq)
    random.shuffle(seq)
    return seq


def make_full_solution():
    rows = [g * 3 + r for g in shuffled(range(3)) for r in shuffled(range(3))]
    cols = [g * 3 + c for g in shuffled(range(3)) for c in shuffled(range(3))]
    nums = shuffled(DIGITS)

    return [[nums[pattern(r, c)] for c in cols] for r in rows]


def get_candidates(board, r, c):
    if board[r][c] != 0:
        return []

    used = set(board[r])
    used.update(board[i][c] for i in range(9))

    br = r // 3 * 3
    bc = c // 3 * 3

    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            used.add(board[i][j])

    return [n for n in DIGITS if n not in used]


def find_empty(board):
    best = None
    best_candidates = None

    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                candidates = get_candidates(board, r, c)

                if best is None or len(candidates) < len(best_candidates):
                    best = (r, c)
                    best_candidates = candidates

                if len(best_candidates) == 1:
                    return best, best_candidates

    return best, best_candidates


def solve_count(board, limit=2):
    board = deepcopy(board)
    count = 0

    def backtrack():
        nonlocal count

        if count >= limit:
            return

        pos, candidates = find_empty(board)

        if pos is None:
            count += 1
            return

        r, c = pos
        random.shuffle(candidates)

        for n in candidates:
            board[r][c] = n
            backtrack()
            board[r][c] = 0

            if count >= limit:
                return

    backtrack()
    return count


def make_puzzle(clues):
    solution = make_full_solution()
    puzzle = deepcopy(solution)

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    target_remove = 81 - clues
    removed = 0

    for r, c in cells:
        if removed >= target_remove:
            break

        old = puzzle[r][c]
        puzzle[r][c] = 0

        if solve_count(puzzle, limit=2) == 1:
            removed += 1
        else:
            puzzle[r][c] = old

    return puzzle, solution


# =========================
# 游戏状态
# =========================

def normalize_input(value):
    value = str(value).strip()

    if value == "":
        return 0

    if value in "123456789" and len(value) == 1:
        return int(value)

    return -1


def blank_grid():
    return [[0 for _ in range(9)] for _ in range(9)]


def start_new_game(difficulty):
    puzzle, solution = make_puzzle(DIFFICULTY_CLUES[difficulty])

    st.session_state.difficulty = difficulty
    st.session_state.puzzle = puzzle
    st.session_state.solution = solution
    st.session_state.prefill = blank_grid()
    st.session_state.message = ""
    st.session_state.start_time = time.time()
    st.session_state.hints_used = 0
    st.session_state.game_id = st.session_state.get("game_id", 0) + 1


def get_current_grid():
    """
    读取当前界面上的输入。
    注意：这里不修改输入框的 session_state，只读取。
    """
    puzzle = st.session_state.puzzle
    grid = deepcopy(puzzle)
    game_id = st.session_state.game_id

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] == 0:
                key = f"cell_{game_id}_{r}_{c}"
                value = st.session_state.get(key, "")

                if value == "":
                    value = st.session_state.prefill[r][c]

                grid[r][c] = normalize_input(value)

    return grid


def save_current_to_prefill():
    grid = get_current_grid()

    for r in range(9):
        for c in range(9):
            if st.session_state.puzzle[r][c] == 0:
                value = grid[r][c]
                st.session_state.prefill[r][c] = value if value in DIGITS else 0


def has_conflict(grid, r, c, val):
    if val <= 0:
        return False

    for j in range(9):
        if j != c and grid[r][j] == val:
            return True

    for i in range(9):
        if i != r and grid[i][c] == val:
            return True

    br = r // 3 * 3
    bc = c // 3 * 3

    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if (i, j) != (r, c) and grid[i][j] == val:
                return True

    return False

def find_duplicate_cells(grid):
    """
    找出所有重复数字所在的格子。
    只要某行、某列、某个 3x3 宫内有重复，就把相关格子加入集合。
    """
    duplicate_cells = set()

    def check_unit(cells):
        seen = {}

        for r, c in cells:
            v = grid[r][c]

            if v in DIGITS:
                seen.setdefault(v, []).append((r, c))

        for positions in seen.values():
            if len(positions) > 1:
                for pos in positions:
                    duplicate_cells.add(pos)

    # 检查每一行
    for r in range(9):
        check_unit([(r, c) for c in range(9)])

    # 检查每一列
    for c in range(9):
        check_unit([(r, c) for r in range(9)])

    # 检查每个 3x3 宫
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            check_unit([
                (r, c)
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            ])

    return duplicate_cells

def check_answer():
    grid = get_current_grid()
    solution = st.session_state.solution

    invalid = []
    conflict = []
    wrong = []
    empty_count = 0

    for r in range(9):
        for c in range(9):
            v = grid[r][c]

            if v == 0:
                empty_count += 1
            elif v == -1:
                invalid.append((r + 1, c + 1))
            elif has_conflict(grid, r, c, v):
                conflict.append((r + 1, c + 1))
            elif v != solution[r][c]:
                wrong.append((r + 1, c + 1))

    if invalid:
        st.session_state.message = f"有非法输入，只能填 1-9。位置：{invalid[:8]}"
    elif conflict:
        st.session_state.message = f"有重复冲突。前几个位置：{conflict[:8]}"
    elif wrong:
        st.session_state.message = f"有 {len(wrong)} 个格子不正确。前几个位置：{wrong[:8]}"
    elif empty_count > 0:
        st.session_state.message = f"目前没有发现错误，还剩 {empty_count} 个空格。"
    else:
        elapsed = int(time.time() - st.session_state.start_time)
        minute, second = divmod(elapsed, 60)

        st.session_state.message = (
            f"完成。用时 {minute} 分 {second} 秒，"
            f"使用提示 {st.session_state.hints_used} 次。"
        )


def give_hint():
    save_current_to_prefill()

    puzzle = st.session_state.puzzle
    solution = st.session_state.solution
    prefill = st.session_state.prefill

    empty_cells = []

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] == 0 and prefill[r][c] == 0:
                empty_cells.append((r, c))

    if not empty_cells:
        st.session_state.message = "没有空格可以提示。"
        return

    r, c = random.choice(empty_cells)
    prefill[r][c] = solution[r][c]

    st.session_state.hints_used += 1
    st.session_state.message = f"提示：第 {r + 1} 行，第 {c + 1} 列填 {solution[r][c]}。"
    st.session_state.game_id += 1


def clear_inputs():
    st.session_state.prefill = blank_grid()
    st.session_state.message = "已清空本局填写内容。"
    st.session_state.game_id += 1


def show_solution():
    puzzle = st.session_state.puzzle
    solution = st.session_state.solution

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] == 0:
                st.session_state.prefill[r][c] = solution[r][c]

    st.session_state.message = "已显示答案。"
    st.session_state.game_id += 1


# =========================
# 页面
# =========================

st.set_page_config(
    page_title="数独游戏",
    page_icon="🧩",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 900px;
        padding-top: 1rem;
    }

    div[data-testid="stTextInput"] input {
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        height: 48px;
        padding: 0;
        border-radius: 3px;
    }

    div[data-testid="stTextInput"] label {
        display: none;
    }

    .thick-line {
        border-bottom: 3px solid #222;
        margin: 8px 0 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "puzzle" not in st.session_state:
    start_new_game("中等")


st.title("数独游戏")
st.caption("规则：每行、每列、每个 3×3 宫内填入 1–9，且不能重复。")


# =========================
# 侧边栏
# =========================

with st.sidebar:
    st.header("设置")

    difficulty = st.selectbox(
        "难度",
        list(DIFFICULTY_CLUES.keys()),
        index=list(DIFFICULTY_CLUES.keys()).index(st.session_state.difficulty),
    )

    if st.button("新游戏", use_container_width=True):
        start_new_game(difficulty)
        st.rerun()

    st.divider()

    if st.button("检查答案", use_container_width=True):
        check_answer()

    if st.button("给一个提示", use_container_width=True):
        give_hint()
        st.rerun()

    if st.button("清空本局", use_container_width=True):
        clear_inputs()
        st.rerun()

    if st.button("显示答案", use_container_width=True):
        show_solution()
        st.rerun()

    st.divider()

    elapsed = int(time.time() - st.session_state.start_time)
    minute, second = divmod(elapsed, 60)

    st.write(f"当前难度：{st.session_state.difficulty}")
    st.write(f"用时：{minute:02d}:{second:02d}")
    st.write(f"提示次数：{st.session_state.hints_used}")


# =========================
# 棋盘
# =========================

st.subheader(f"当前难度：{st.session_state.difficulty}")

puzzle = st.session_state.puzzle
prefill = st.session_state.prefill
game_id = st.session_state.game_id

# 找出重复格子
current_grid = get_current_grid()
duplicate_cells = find_duplicate_cells(current_grid)

# 给重复格子加橙色边框
conflict_css = []

for r, c in duplicate_cells:
    conflict_css.append(
        f"""
        div[data-testid="stTextInput"]:has(input[aria-label="cell-{game_id}-{r}-{c}"]) input,
        div[data-testid="stTextInput"]:has(input[aria-label="fixed-{game_id}-{r}-{c}"]) input {{
            border: 3px solid #ff9800 !important;
            box-shadow: 0 0 0 1px #ff9800 !important;
            background-color: #fff7e6 !important;
        }}
        """
    )

if conflict_css:
    st.markdown(
        "<style>" + "\n".join(conflict_css) + "</style>",
        unsafe_allow_html=True,
    )

for r in range(9):
    cols = st.columns(9, gap="small")

    for c in range(9):
        with cols[c]:
            if puzzle[r][c] != 0:
                st.text_input(
                    label=f"fixed-{game_id}-{r}-{c}",
                    value=str(puzzle[r][c]),
                    disabled=True,
                    key=f"fixed_{game_id}_{r}_{c}",
                    label_visibility="collapsed",
                )
            else:
                default_value = "" if prefill[r][c] == 0 else str(prefill[r][c])

                st.text_input(
                    label=f"cell-{game_id}-{r}-{c}",
                    value=default_value,
                    max_chars=1,
                    key=f"cell_{game_id}_{r}_{c}",
                    label_visibility="collapsed",
                )

    if r in [2, 5]:
        st.markdown('<div class="thick-line"></div>', unsafe_allow_html=True)


# =========================
# 信息提示
# =========================

if st.session_state.message:
    msg = st.session_state.message

    if msg.startswith("完成"):
        st.success(msg)
    elif msg.startswith("提示") or msg.startswith("已") or "没有发现错误" in msg:
        st.info(msg)
    else:
        st.warning(msg)
