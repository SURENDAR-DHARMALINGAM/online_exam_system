# ==============================
# ONLINE EXAMINATION SYSTEM
# SINGLE FILE – FULL VERSION (MCQ + Coding)
# ==============================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import time

# ---------- DATABASE ----------
conn = sqlite3.connect("exam.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS exams(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    duration INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    question TEXT,
    o1 TEXT,
    o2 TEXT,
    o3 TEXT,
    o4 TEXT,
    correct TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS results(
    student TEXT,
    exam TEXT,
    question TEXT,
    chosen TEXT,
    correct TEXT
)
""")

cur.execute("""
INSERT OR IGNORE INTO users
(name,username,password,role)
VALUES('Administrator','admin','admin','admin')
""")

conn.commit()



# ---------- GLOBAL ----------
root = tk.Tk()
root.title("Online Examination System")
root.geometry("900x650")

theme = {"bg": "#121212", "fg": "#ffffff", "card": "#1e1e1e"}

student = ""
exam = None
qs = []
idx = 0
answers = {}
time_left = 0

# ---------- UI HELPERS ----------
def clear():
    for w in root.winfo_children(): w.destroy()
def card(parent):
    f = tk.Frame(parent, bg=theme["card"], padx=15, pady=15)
    f.pack(pady=10, fill="x", padx=20)
    return f
def apply(widget):
    for w in widget.winfo_children():
        try:
            if isinstance(w, (tk.Label, tk.Button, tk.Radiobutton)):
                w.config(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(w, tk.Entry):
                w.config(bg="#333", fg="#fff", insertbackground="white")
            elif isinstance(w, tk.Text):
                w.config(bg="#333", fg="#fff", insertbackground="white")
        except tk.TclError:
            pass  # skip widgets that don't support these options
        # recursively apply to frames or containers
        if isinstance(w, tk.Frame):
            apply(w)


# ---------- HOME ----------
def home():
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root, text="Online Examination System", font=("Segoe UI",26,"bold")).pack(pady=30)
    tk.Button(root, text="Login as Student", width=20, command=student_login).pack(pady=10)
    tk.Button(root, text="Login as Admin", width=20, command=admin_login).pack(pady=10)
    apply(root)

# ---------- LOGIN ----------
def student_login(): login("student")
def admin_login(): login("admin")
def login(role):
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root, text=f"{role.title()} Login", font=("Segoe UI",22,"bold")).pack(pady=20)
    f = card(root)
    tk.Label(f, text="Username").pack(anchor="w"); u = tk.Entry(f); u.pack(fill="x")
    tk.Label(f, text="Password").pack(anchor="w", pady=(10,0)); p = tk.Entry(f, show="*"); p.pack(fill="x")
    def check():
        global student
        cur.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (u.get(),p.get(),role))
        r = cur.fetchone()
        if not r: messagebox.showerror("Error","Invalid credentials"); return
        if role=="student": student=u.get(); exam_list()
        else: admin_panel()
    tk.Button(f, text="Login", command=check).pack(pady=15)
    tk.Button(root, text="Back", command=home).pack()
    apply(root)

# ---------- ADMIN PANEL ----------
def admin_panel():
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root, text="Admin Panel", font=("Segoe UI",22,"bold")).pack(pady=15)
    buttons=[("Create Student ID", create_student),
             ("Create Exam", create_exam),
             ("Manage Exams", manage_exams),
             ("View Results", view_results),
             ("Score Analytics", score_analytics),
             ("Edit Profile", edit_admin),
             ("Logout", home)]
    for t,c in buttons: tk.Button(root,text=t,width=25,command=c).pack(pady=5)
    apply(root)

# ---------- CREATE STUDENT ----------
def create_student():
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root, text="Create Student", font=("Segoe UI",22,"bold")).pack(pady=15)
    f = card(root)
    tk.Label(f, text="Student Name").pack(anchor="w"); name=tk.Entry(f); name.pack(fill="x")
    tk.Label(f, text="Username").pack(anchor="w"); u=tk.Entry(f); u.pack(fill="x")
    tk.Label(f, text="Password").pack(anchor="w"); p=tk.Entry(f); p.pack(fill="x")
    def save():
        try: cur.execute("INSERT INTO users VALUES(NULL,?,?,?,'student')",(name.get(),u.get(),p.get())); conn.commit(); messagebox.showinfo("Success","Student created")
        except: messagebox.showerror("Error","Username exists")
    tk.Button(f,text="Create", command=save).pack(pady=10)
    tk.Button(root,text="Back", command=admin_panel).pack()
    apply(root)

# ---------- CREATE EXAM ----------
def create_exam():
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root,text="Create Exam", font=("Segoe UI",22,"bold")).pack(pady=10)
    f = card(root)
    tk.Label(f,text="Exam Name").pack(anchor="w"); en=tk.Entry(f); en.pack(fill="x")
    tk.Label(f,text="Duration (minutes)").pack(anchor="w"); dur=tk.Entry(f); dur.pack(fill="x")
    def save_exam():
        cur.execute("INSERT INTO exams VALUES(NULL,?,?)",(en.get(),int(dur.get())))
        conn.commit(); add_questions(cur.lastrowid)
    tk.Button(f,text="Next: Add Questions", command=save_exam).pack(pady=10)
    tk.Button(root,text="Back", command=admin_panel).pack()
    apply(root)

# ---------- ADD QUESTIONS ----------
def add_questions(exam_id):
    clear()
    root.configure(bg=theme["bg"])

    tk.Label(root, text="Add Question", font=("Segoe UI", 22, "bold")).pack(pady=10)
    f = card(root)

    # Question field (multi-line)
    tk.Label(f, text="Question").pack(anchor="w")
    q = tk.Text(f, height=4)
    q.pack(fill="x")

    # Options
    opts = []
    for i in range(4):
        tk.Label(f, text=f"Option {i+1}").pack(anchor="w")
        e = tk.Entry(f)
        e.pack(fill="x")
        opts.append(e)

    # Correct answer
    tk.Label(f, text="Correct Answer (1-4)").pack(anchor="w")
    cor = ttk.Combobox(f, values=[1, 2, 3, 4])
    cor.pack(fill="x")
    cor.current(0)

    # Save question
    def save_q():
        try:
            question_text = q.get("1.0", tk.END).strip()
            correct_index = int(cor.get()) - 1
            correct_answer = opts[correct_index].get()

            # Validate inputs
            if not question_text:
                messagebox.showerror("Error", "Question cannot be empty")
                return
            if any(not o.get() for o in opts):
                messagebox.showerror("Error", "All options must be filled")
                return

            # Insert into database
            cur.execute("""INSERT INTO questions
                           (id, exam_id, question, o1, o2, o3, o4, correct)
                           VALUES(NULL,?,?,?,?,?,?,?)""",
                        (exam_id,
                         question_text,
                         opts[0].get(),
                         opts[1].get(),
                         opts[2].get(),
                         opts[3].get(),
                         correct_answer))
            conn.commit()
            messagebox.showinfo("Saved", "Question added successfully!")

            # Clear fields for next question
            q.delete("1.0", tk.END)
            for o in opts:
                o.delete(0, tk.END)
            cor.current(0)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(f, text="Add Question", command=save_q).pack(pady=5)
    tk.Button(root, text="Finish", command=admin_panel).pack(pady=10)
    apply(root)

# ---------- EXAM LIST ----------
def exam_list():
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root,text="Select Exam", font=("Segoe UI",22,"bold")).pack(pady=10)
    cur.execute("SELECT * FROM exams")
    for e in cur.fetchall(): tk.Button(root,text=e[1],width=30, command=lambda x=e:start_exam(x)).pack(pady=5)
    tk.Button(root,text="Logout", command=home).pack(pady=10)
    apply(root)

# ---------- START EXAM ----------
def start_exam(e):
    global exam, qs, idx, answers, time_left
    exam = e
    idx = 0
    answers = {}

    cur.execute("SELECT * FROM questions WHERE exam_id=?", (e[0],))
    qs = cur.fetchall()

    if not qs:
        messagebox.showerror("Error", "No questions found")
        return

    time_left = e[2] * 60
    exam_ui()


def exam_ui():
    clear()
    root.configure(bg=theme["bg"])

    tk.Label(
        root,
        text=exam[1],
        font=("Segoe UI", 20, "bold"),
        bg=theme["bg"],
        fg=theme["fg"]
    ).pack(pady=5)

    timer_lbl = tk.Label(
        root,
        font=("Segoe UI", 14, "bold"),
        fg="red",
        bg=theme["bg"]
    )
    timer_lbl.pack()

    pb = ttk.Progressbar(root, length=500, maximum=len(qs))
    pb.pack(pady=5)

    # ----- QUESTION CARD -----
    f = card(root)

    q_box = tk.Text(
        f,
        height=5,
        wrap="word",
        font=("Segoe UI", 14),
        bg=theme["card"],
        fg=theme["fg"],
        relief="flat"
    )
    q_box.pack(fill="x", pady=10)
    q_box.config(state="disabled")

    # 🔥 IMPORTANT: keep StringVar persistent
    choice = tk.StringVar()

    rb = []

    # ----- NAV -----
    nav = tk.Frame(root, bg=theme["bg"])
    nav.pack(pady=10)

    prev_btn = tk.Button(nav, text="⬅ Previous", width=12)
    next_btn = tk.Button(nav, text="Next ➡", width=12)
    submit_btn = tk.Button(nav, text="Submit", bg="green", fg="white", width=12)

    prev_btn.grid(row=0, column=0, padx=5)
    next_btn.grid(row=0, column=1, padx=5)
    submit_btn.grid(row=0, column=2, padx=5)

    # ----- LOAD QUESTION -----
    def load_q():
        q = qs[idx]

        q_box.config(state="normal")
        q_box.delete("1.0", tk.END)
        q_box.insert(tk.END, f"Q{idx+1}. {q[2]}")
        q_box.config(state="disabled")

        for r in rb:
            r.destroy()
        rb.clear()

        for i in range(4):
            r = tk.Radiobutton(
                f,
                text=q[3+i],
                variable=choice,
                value=q[3+i],
                font=("Segoe UI", 12),
                bg=theme["card"],
                fg=theme["fg"],
                activebackground=theme["card"],
                activeforeground=theme["fg"],
                selectcolor="#4CAF50",   # ✅ FIX: visible selection
                indicatoron=True,
                wraplength=650,
                anchor="w",
                justify="left",
                padx=10,
                pady=6
            )
            r.pack(fill="x", pady=4)
            rb.append(r)

        # 🔥 restore saved answer
        choice.set(answers.get(idx, ""))

        pb["value"] = idx + 1
        prev_btn["state"] = "normal" if idx > 0 else "disabled"
        next_btn["state"] = "normal" if idx < len(qs) - 1 else "disabled"

    def save():
        answers[idx] = choice.get()

    def next_q():
        global idx
        save()
        idx += 1
        load_q()

    def prev_q():
        global idx
        save()
        idx -= 1
        load_q()

    def submit():
        save()

        cur.execute(
            "DELETE FROM results WHERE student=? AND exam=?",
            (student, exam[1])
        )

        score = 0
        for i, q in enumerate(qs):
            sel = answers.get(i, "")
            cor = q[7]
            if sel == cor:
                score += 1

            cur.execute(
                "INSERT INTO results VALUES(?,?,?,?,?)",
                (student, exam[1], q[2], sel, cor)
            )

        conn.commit()
        messagebox.showinfo(
            "Submitted",
            f"Score: {score}/{len(qs)}"
        )
        student_result()

    prev_btn.config(command=prev_q)
    next_btn.config(command=next_q)
    submit_btn.config(command=submit)

    def tick():
        global time_left
        if time_left <= 0:
            submit()
            return
        m, s = divmod(time_left, 60)
        timer_lbl.config(text=f"⏳ {m:02d}:{s:02d}")
        time_left -= 1
        root.after(1000, tick)

    load_q()
    tick()
    apply(root)



# ---------- STUDENT RESULT ----------
def student_result():
    clear()
    root.configure(bg=theme["bg"])

    tk.Label(root, text="Your Result", font=("Segoe UI", 22, "bold")).pack(pady=10)

    cur.execute("SELECT question, chosen, correct FROM results WHERE student=?", (student,))
    rows = cur.fetchall()

    score = 0
    for q, ch, co in rows:
        c = card(root)
        tk.Label(c, text=q, wraplength=700).pack(anchor="w")
        tk.Label(c, text=f"Your Answer: {ch}", fg="orange").pack(anchor="w")
        tk.Label(c, text=f"Correct Answer: {co}", fg="lightgreen").pack(anchor="w")
        if ch == co:
            score += 1

    tk.Label(
        root,
        text=f"Final Score: {score}/{len(rows)}",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    tk.Button(root, text="Logout", command=home).pack(pady=10)
    apply(root)


# ---------- ADMIN RESULTS ----------
def view_results():
    clear(); root.configure(bg=theme["bg"])
    tk.Label(root,text="All Results", font=("Segoe UI",22,"bold")).pack(pady=10)
    cur.execute("SELECT student,exam,SUM(chosen=correct),COUNT(*) FROM results GROUP BY student,exam")
    for s,e,sc,tot in cur.fetchall():
        c=card(root); tk.Label(c,text=f"{s} | {e}").pack(anchor="w"); tk.Label(c,text=f"Score: {sc}/{tot}").pack(anchor="w")
    tk.Button(root,text="Back",command=admin_panel).pack(pady=10); apply(root)

# ---------- ANALYTICS ----------
def score_analytics():
    clear(); root.configure(bg=theme["bg"]); tk.Label(root,text="Score Analytics", font=("Segoe UI",22,"bold")).pack(pady=10)
    cur.execute("SELECT exam,COUNT(DISTINCT student),SUM(chosen=correct)*100.0/COUNT(*) FROM results GROUP BY exam")
    for e,a,avg in cur.fetchall(): c=card(root); tk.Label(c,text=f"Exam: {e}").pack(anchor="w"); tk.Label(c,text=f"Attempts: {a}").pack(anchor="w"); pb=ttk.Progressbar(c,length=400); pb.pack(); pb["value"]=avg
    tk.Button(root,text="Back", command=admin_panel).pack(pady=10); apply(root)

# ---------- ADMIN EDIT ----------
def edit_admin():
    clear()
    root.configure(bg=theme["bg"])

    tk.Label(
        root,
        text="Edit Admin Profile",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=10)

    f = card(root)

    # 🔹 Fetch existing admin data
    cur.execute("SELECT name, username, password FROM users WHERE role='admin' LIMIT 1")
    admin = cur.fetchone()

    tk.Label(f, text="Name").pack(anchor="w")
    name = tk.Entry(f)
    name.pack(fill="x")
    name.insert(0, admin[0])

    tk.Label(f, text="Username").pack(anchor="w")
    user = tk.Entry(f)
    user.pack(fill="x")
    user.insert(0, admin[1])

    tk.Label(f, text="Password").pack(anchor="w")
    pwd = tk.Entry(f)
    pwd.pack(fill="x")
    pwd.insert(0, admin[2])

    def save():
        if not name.get() or not user.get() or not pwd.get():
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            cur.execute("""
                UPDATE users
                SET name=?, username=?, password=?
                WHERE role='admin'
            """, (name.get(), user.get(), pwd.get()))
            conn.commit()
            messagebox.showinfo("Success", "Admin profile updated successfully")
            admin_panel()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    tk.Button(f, text="Save Changes", command=save).pack(pady=10)
    tk.Button(root, text="Back", command=admin_panel).pack()

    apply(root)


# ---------- MANAGE EXAMS ----------
def manage_exams():
    clear()
    root.configure(bg=theme["bg"])

    tk.Label(root, text="Manage Exams",
             font=("Segoe UI", 22, "bold")).pack(pady=10)

    cur.execute("SELECT id, name, duration FROM exams")
    exams = cur.fetchall()

    for exam_id, exam_name, exam_duration in exams:
        c = card(root)

        tk.Label(
            c,
            text=f"{exam_name} | Duration: {exam_duration} min",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Button(
            c, text="Edit",
            command=lambda eid=exam_id: edit_exam(eid)
        ).pack(side="left", padx=5)

        tk.Button(
            c, text="Delete",
            command=lambda eid=exam_id: delete_exam(eid)
        ).pack(side="left", padx=5)

    tk.Button(root, text="Back", command=admin_panel).pack(pady=10)
    apply(root)


# ---------- EDIT EXAM + QUESTIONS ----------
def edit_exam(exam_id):
    clear()
    root.configure(bg=theme["bg"])

    tk.Label(root, text="Edit Exam & Questions",
             font=("Segoe UI", 22, "bold")).pack(pady=10)

    # ---------- SCROLLABLE AREA ----------
    canvas = tk.Canvas(root, bg=theme["bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=theme["bg"])

    frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---------- EXAM INFO ----------
    cur.execute("SELECT name, duration FROM exams WHERE id=?", (exam_id,))
    exam_name, exam_duration = cur.fetchone()

    ec = card(frame)
    tk.Label(ec, text="Exam Name").pack(anchor="w")
    en = tk.Entry(ec); en.pack(fill="x")
    en.insert(0, exam_name)

    tk.Label(ec, text="Duration (minutes)").pack(anchor="w")
    dur = tk.Entry(ec); dur.pack(fill="x")
    dur.insert(0, exam_duration)

    def save_exam():
        cur.execute(
            "UPDATE exams SET name=?, duration=? WHERE id=?",
            (en.get(), int(dur.get()), exam_id)
        )
        conn.commit()
        messagebox.showinfo("Saved", "Exam updated")

    tk.Button(ec, text="Save Exam", command=save_exam).pack(pady=5)

    # ---------- LOAD QUESTIONS ----------
    cur.execute("""
        SELECT id, question, o1, o2, o3, o4, correct
        FROM questions WHERE exam_id=?
    """, (exam_id,))
    questions = cur.fetchall()

    if not questions:
        tk.Label(frame, text="No questions found",
                 fg="red", font=("Segoe UI", 12)).pack(pady=10)

    for qid, qtext, o1, o2, o3, o4, correct in questions:
        qc = card(frame)

        qt = tk.Text(qc, height=4)
        qt.pack(fill="x")
        qt.insert("1.0", qtext)

        opts = []
        for val in (o1, o2, o3, o4):
            e = tk.Entry(qc)
            e.pack(fill="x", pady=2)
            e.insert(0, val)
            opts.append(e)

        cor = ttk.Combobox(qc, values=[1, 2, 3, 4], width=5, state="readonly")
        cor.pack(anchor="w", pady=5)
        cor.set(str([o1, o2, o3, o4].index(correct) + 1))

        def save_q(qid=qid, qt=qt, opts=opts, cor=cor):
            correct_ans = opts[int(cor.get()) - 1].get()
            cur.execute("""
                UPDATE questions
                SET question=?, o1=?, o2=?, o3=?, o4=?, correct=?
                WHERE id=?
            """, (
                qt.get("1.0", tk.END).strip(),
                opts[0].get(), opts[1].get(),
                opts[2].get(), opts[3].get(),
                correct_ans, qid
            ))
            conn.commit()
            messagebox.showinfo("Saved", "Question updated")

        def delete_q(qid=qid):
            if messagebox.askyesno("Delete", "Delete this question?"):
                cur.execute("DELETE FROM questions WHERE id=?", (qid,))
                conn.commit()
                edit_exam(exam_id)

        b = tk.Frame(qc, bg=theme["card"])
        b.pack(anchor="w", pady=5)

        tk.Button(b, text="Save Question", command=save_q)\
            .pack(side="left", padx=5)
        tk.Button(b, text="Delete", command=delete_q)\
            .pack(side="left", padx=5)

    # ---------- FIXED BOTTOM BUTTON BAR ----------
    bottom = tk.Frame(root, bg=theme["bg"])
    bottom.pack(side="bottom", fill="x", pady=10)

    tk.Button(
        bottom,
        text="➕ Add New Question",
        command=lambda: add_questions(exam_id)
    ).pack(side="left", padx=20)

    tk.Button(
        bottom,
        text="⬅ Back to Manage Exams",
        command=manage_exams
    ).pack(side="right", padx=20)

    apply(root)




# ---------- START ----------
home(); root.mainloop()
