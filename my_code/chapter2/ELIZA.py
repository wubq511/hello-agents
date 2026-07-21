import re
import random
from dataclasses import dataclass, field

# ============================================================
# 1. 情感词表（轻量规则式情感分析）
# ============================================================
emotion_lexicon = {
    # positive
    "happy": 1, "glad": 1, "great": 1, "wonderful": 1, "good": 1,
    "fantastic": 1, "pleased": 1, "excited": 1, "joy": 1, "joyful": 1,
    "love": 1, "loved": 1, "like": 1, "liked": 1, "enjoy": 1, "enjoyed": 1,
    "better": 1, "fine": 1, "okay": 1, "ok": 1, "nice": 1, "proud": 1,
    "grateful": 1, "hopeful": 1, "relieved": 1, "calm": 1, "peaceful": 1,
    "confident": 1, "comfortable": 1, "satisfied": 1,
    # negative
    "sad": -1, "depressed": -1, "awful": -1, "terrible": -1, "bad": -1,
    "horrible": -1, "miserable": -1, "unhappy": -1, "upset": -1, "angry": -1,
    "furious": -1, "mad": -1, "anxious": -1, "worried": -1, "afraid": -1,
    "scared": -1, "lonely": -1, "alone": -1, "hopeless": -1, "helpless": -1,
    "frustrated": -1, "annoyed": -1, "tired": -1, "exhausted": -1,
    "confused": -1, "lost": -1, "hate": -1, "hated": -1, "dislike": -1,
    "stressed": -1, "overwhelmed": -1, "pain": -1, "hurt": -1, "cry": -1,
    "crying": -1, "fail": -1, "failed": -1, "fear": -1,
}


def analyze_emotion(text: str) -> str:
    """对输入文本做词级情感极性判断，返回 'positive' / 'negative' / 'neutral'"""
    words = re.findall(r'\b\w+\b', text.lower())
    score = sum(emotion_lexicon.get(w, 0) for w in words)
    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    return "neutral"


# ============================================================
# 2. 代词转换规则（增强版）
# ============================================================
pronoun_swap = {
    "i": "you", "you": "i", "me": "you", "my": "your", "your": "my",
    "am": "are", "are": "am", "was": "were", "were": "was",
    "i'd": "you would", "you'd": "i would",
    "i've": "you have", "you've": "i have",
    "i'll": "you will", "you'll": "i will",
    "i'm": "you're", "you're": "i'm",
    "yours": "mine", "mine": "yours",
    "myself": "yourself", "yourself": "myself",
    "ourselves": "yourselves", "yourselves": "ourselves",
}


def swap_pronouns(phrase: str) -> str:
    """对输入短语中的代词进行第一/第二人称转换，保留首词大小写"""
    words = phrase.split()
    if not words:
        return phrase
    swapped = [pronoun_swap.get(w.lower(), w) for w in words]
    # 恢复首词大小写
    if words[0][0].isupper() and swapped:
        swapped[0] = swapped[0][0].upper() + swapped[0][1:] if len(swapped[0]) > 1 else swapped[0].upper()
    return " ".join(swapped)


# ============================================================
# 3. 规则库（按优先级排序，高优先级先匹配）
# ============================================================
# 每条规则: (priority, pattern, response_templates)
rules = [
    # --- 高优先级：具体关键词模式 ---
    (20, r'I feel (.*)', [
        "Why do you feel {0}?",
        "How long have you felt {0}?",
        "What do you think is causing you to feel {0}?",
        "Does feeling {0} come up often?",
        "What would help you not feel {0}?",
        "When you feel {0}, what do you usually do?",
    ]),
    (20, r'I am (.*)', [
        "Did you come to me because you are {0}?",
        "How long have you been {0}?",
        "How do you feel about being {0}?",
        "What does being {0} mean to you?",
        "Do you enjoy being {0}?",
        "What led to you being {0}?",
    ]),
    (18, r'I need (.*)', [
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "Are you sure you need {0}?",
        "What would happen if you never got {0}?",
        "Is needing {0} something new for you?",
    ]),
    (18, r'I want (.*)', [
        "Why do you want {0}?",
        "What would it mean to you if you got {0}?",
        "What's stopping you from getting {0}?",
        "Have you tried to get {0} before?",
        "How important is {0} to you?",
    ]),
    (18, r'I (?:don\'t|do not) want (.*)', [
        "Why don't you want {0}?",
        "What would happen if you got {0} anyway?",
        "Is there something about {0} that bothers you?",
        "What would you prefer instead of {0}?",
    ]),
    (16, r'Why don\'t you (.*)\?', [
        "Do you really think I don't {0}?",
        "Perhaps eventually I will {0}.",
        "Do you really want me to {0}?",
        "What makes you think I wouldn't {0}?",
        "Would it help if I {0}?",
    ]),
    (16, r'Why can\'t I (.*)\?', [
        "Do you think you should be able to {0}?",
        "If you could {0}, what would you do?",
        "I don't know -- why can't you {0}?",
        "What's preventing you from {0}?",
        "Have you tried {0} before?",
    ]),
    (15, r'I can\'t (.*)', [
        "Why can't you {0}?",
        "Have you tried?",
        "What's holding you back from {0}?",
        "Maybe you could {0} if you tried differently.",
        "What would it take for you to {0}?",
    ]),
    (15, r'I (?:can|could) (.*)', [
        "What makes you think you can {0}?",
        "You seem quite confident about being able to {0}.",
        "Have you {0} before?",
        "What would it look like if you {0}?",
    ]),
    # --- 情绪词 ---
    (14, r'I(?:\'m| am) (?:sad|depressed|unhappy|down|upset|miserable)', [
        "I'm sorry to hear that. Can you tell me more about what's making you feel this way?",
        "That sounds really difficult. How long have you been feeling like this?",
        "What do you think is behind these feelings?",
        "Sometimes talking about it can help. What's been going on?",
    ]),
    (14, r'I(?:\'m| am) (?:happy|glad|great|wonderful|excited|fantastic)', [
        "That's wonderful! What's contributing to these positive feelings?",
        "It's great to hear that. What's making you feel so good?",
        "Tell me more about what's bringing you joy.",
        "I'm glad to hear that. How can you hold on to this feeling?",
    ]),
    (14, r'I(?:\'m| am) (?:angry|furious|mad|annoyed)', [
        "What's making you feel so angry?",
        "Anger can be a powerful signal. What do you think it's telling you?",
        "What happened that led to these feelings?",
        "How do you usually express your anger?",
    ]),
    (14, r'I(?:\'m| am) (?:afraid|scared|frightened|anxious|worried)', [
        "What are you afraid of?",
        "Fear often points to something we care about. What might that be?",
        "When did you first start feeling this way?",
        "What do you think would help you feel less anxious?",
    ]),
    # --- 人际关系 ---
    (12, r'.*\b(?:mother|mom|mama)\b.*', [
        "Tell me more about your mother.",
        "What was your relationship with your mother like?",
        "How do you feel about your mother?",
        "What memories come to mind when you think of your mother?",
        "How has your mother influenced who you are?",
        "Does your mother still play a big role in your life?",
    ]),
    (12, r'.*\b(?:father|dad|papa)\b.*', [
        "Tell me more about your father.",
        "How did your father make you feel?",
        "What has your father taught you?",
        "What's your relationship with your father like now?",
        "How would you describe your father?",
    ]),
    (12, r'.*\b(?:friend|friends|buddy|buddies)\b.*', [
        "Tell me more about your friends.",
        "How do your friends make you feel?",
        "Are you satisfied with your friendships?",
        "What qualities do you value in a friend?",
        "Has something happened with a friend recently?",
    ]),
    (12, r'.*\b(?:wife|husband|partner|girlfriend|boyfriend|spouse)\b.*', [
        "Tell me more about your partner.",
        "How is your relationship going?",
        "What do you find most challenging about your relationship?",
        "What do you appreciate most about your partner?",
        "How long have you been together?",
    ]),
    (12, r'.*\b(?:boss|manager|supervisor|coworker|colleague)\b.*', [
        "Tell me more about your work relationships.",
        "How does that person make you feel?",
        "What's your work environment like?",
        "Have you tried talking to them about it?",
    ]),
    # --- 生活主题 ---
    (10, r'.*\b(?:work|job|career|office)\b.*', [
        "Tell me more about your work.",
        "How do you feel about your job?",
        "Is work a source of stress for you?",
        "What would your ideal work situation look like?",
        "Do you find your work meaningful?",
    ]),
    (10, r'.*\b(?:school|class|study|studying|exam|test|homework)\b.*', [
        "Tell me more about school.",
        "How are your studies going?",
        "Is school causing you stress?",
        "What subjects interest you most?",
        "Do you enjoy learning?",
    ]),
    (10, r'.*\b(?:sleep|dream|nightmare|insomnia)\b.*', [
        "Tell me more about your sleep.",
        "How have you been sleeping lately?",
        "Do you often have dreams like that?",
        "What do you think your dream means?",
        "Are you having trouble falling asleep or staying asleep?",
    ]),
    (10, r'.*\b(?:family|brother|sister|sibling|child|children|kid|kids)\b.*', [
        "Tell me more about your family.",
        "How is your family dynamic?",
        "Who in your family are you closest to?",
        "What's it like growing up in your family?",
    ]),
    # --- 认知词 ---
    (8, r'I think (.*)', [
        "Do you really think {0}?",
        "Why do you think {0}?",
        "What makes you think {0}?",
        "How long have you thought {0}?",
        "Could there be another way to see it besides {0}?",
    ]),
    (8, r'I believe (.*)', [
        "Why do you believe {0}?",
        "What evidence supports your belief that {0}?",
        "Have you always believed {0}?",
        "What would change your mind about {0}?",
    ]),
    (8, r'I remember (.*)', [
        "What makes you remember {0}?",
        "How does remembering {0} make you feel?",
        "When was the last time you thought about {0}?",
        "Is {0} something you think about often?",
    ]),
    (8, r'I forget (.*)', [
        "Why do you think you forget {0}?",
        "Is forgetting {0} a problem for you?",
        "What helps you remember things like {0}?",
    ]),
    # --- 否定/疑问 ---
    (7, r'I don\'t (.*)', [
        "Why don't you {0}?",
        "Is there a reason you don't {0}?",
        "Would you like to {0}?",
        "What would happen if you did {0}?",
    ]),
    (7, r'Are you (.*)\?', [
        "Why do you ask if I'm {0}?",
        "Does it matter to you whether I'm {0}?",
        "What if I were {0}?",
    ]),
    (7, r'Do you (.*)\?', [
        "Why do you ask if I {0}?",
        "Does that question interest you?",
        "What's behind that question?",
    ]),
    (7, r'Can you (.*)\?', [
        "What makes you think I can {0}?",
        "Would you like me to {0}?",
        "Why is {0} important to you?",
    ]),
    # --- 兜底 ---
    (1, r'.*', [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?",
        "That's interesting. Please go on.",
        "I see. And how does that make you feel?",
        "Could you explain that in more detail?",
        "What do you think about that?",
        "How does that relate to what we've been discussing?",
    ]),
]

# 按优先级降序预排序
rules.sort(key=lambda r: r[0], reverse=True)


# ============================================================
# 4. 关键词提取（用于上下文记忆）
# ============================================================
# 需要忽略的停用词
stop_words = {
    "i", "me", "my", "you", "your", "we", "our", "they", "their",
    "am", "is", "are", "was", "were", "be", "been", "being",
    "a", "an", "the", "and", "or", "but", "if", "so", "because",
    "do", "does", "did", "have", "has", "had", "will", "would",
    "can", "could", "should", "shall", "may", "might", "must",
    "not", "no", "don't", "doesn't", "didn't", "won't", "can't",
    "it", "its", "this", "that", "these", "those", "what", "which",
    "who", "whom", "how", "when", "where", "why",
    "very", "really", "just", "also", "too", "then", "than",
    "about", "with", "from", "for", "to", "of", "at", "in", "on",
    "up", "out", "off", "over", "under", "into",
    "feel", "think", "know", "want", "need", "like", "tell",
    "said", "say", "says", "make", "made", "get", "got", "go", "going",
}

# 话题关键词（比停用词更有意义的话题词）
topic_words = {
    "mother", "mom", "father", "dad", "family", "friend", "friends",
    "wife", "husband", "partner", "boss", "work", "job", "school",
    "sleep", "dream", "love", "hate", "angry", "sad", "happy",
    "afraid", "scared", "anxious", "worried", "lonely", "alone",
    "stressed", "tired", "depressed", "confused", "frustrated",
    "relationship", "health", "money", "future", "past", "childhood",
    "children", "life", "death", "change", "hope", "fear", "pain",
}


def extract_topics(text: str) -> set[str]:
    """从文本中提取话题关键词"""
    words = re.findall(r'\b\w+\b', text.lower())
    return set(words) & topic_words


# ============================================================
# 5. 对话上下文
# ============================================================
@dataclass
class ConversationContext:
    history: list[tuple[str, str]] = field(default_factory=list)
    mentioned_topics: set[str] = field(default_factory=set)
    emotion_trajectory: list[str] = field(default_factory=list)
    last_template_index: dict[int, int] = field(default_factory=dict)  # rule_idx -> last chosen template idx
    last_response: str = ""

    def add_turn(self, user_input: str, bot_response: str, emotion: str):
        self.history.append((user_input, bot_response))
        self.mentioned_topics |= extract_topics(user_input)
        self.emotion_trajectory.append(emotion)
        # 只保留最近 5 轮
        if len(self.history) > 5:
            self.history = self.history[-5:]

    @property
    def recent_emotions(self) -> list[str]:
        """最近 3 轮情感"""
        return self.emotion_trajectory[-3:]

    @property
    def consecutive_negative(self) -> int:
        """连续 negative 的轮数"""
        count = 0
        for e in reversed(self.emotion_trajectory):
            if e == "negative":
                count += 1
            else:
                break
        return count


# ============================================================
# 6. 输入预处理
# ============================================================
def preprocess(text: str) -> tuple[str, str]:
    """
    预处理用户输入，返回 (cleaned_text, punctuation_emotion)
    punctuation_emotion: 'strong' / 'confused' / 'normal'
    """
    # 去除首尾空白
    text = text.strip()
    # 多余空格合并
    text = re.sub(r'\s+', ' ', text)
    # 检测标点情感
    punctuation_emotion = "normal"
    if re.search(r'[!?]{3,}', text):
        punctuation_emotion = "strong"
    elif re.search(r'\?{2,}', text):
        punctuation_emotion = "confused"
    # 去除重复标点（保留一个）
    text = re.sub(r'([.!?])\1+', r'\1', text)
    return text, punctuation_emotion


# ============================================================
# 7. 策略引擎
# ============================================================
STRATEGY_FOLLOWUP = "你之前提到过{topic}，能再多说说吗？"
STRATEGY_REPEAT = "我注意到你反复提到{topic}，这对你来说很重要吗？"
STRATEGY_SHORT = "你能多说一些吗？"
STRATEGY_EMOTION_CARE = "你似乎一直不太开心，要不要聊聊什么在困扰你？"
STRATEGY_TOPIC_SWITCH = "我们聊了挺久关于{topic}，要不要换个角度看看？"
STRATEGY_STRONG = "听起来你对此感受很强烈。能告诉我更多吗？"
STRATEGY_CONFUSED = "你似乎有些困惑，能具体说说哪里不明白吗？"

FILLERS = ["Hmm, ", "I see — ", "Well, ", "Let me think... ", ""]
FOLLOW_UPS = [
    " What do you think about that?",
    " How does that make you feel?",
    " Can you say more about that?",
    "",
    "",
]


def apply_strategies(
    base_response: str,
    user_input: str,
    ctx: ConversationContext,
    punctuation_emotion: str,
    enable_strategies: bool = True,
) -> str:
    """在规则匹配结果之上应用策略层"""

    if not enable_strategies:
        return base_response

    # 1. 标点情感增强
    if punctuation_emotion == "strong" and len(user_input) < 30:
        return STRATEGY_STRONG
    if punctuation_emotion == "confused":
        return STRATEGY_CONFUSED

    # 2. 连续负面情感关怀
    if ctx.consecutive_negative >= 3:
        return STRATEGY_EMOTION_CARE

    # 3. 短输入引导
    if len(user_input.split()) < 3:
        return STRATEGY_SHORT

    # 4. 重复检测（与上一轮输入相似）
    if len(ctx.history) >= 1:
        prev_input = ctx.history[-1][0].lower()
        # 简单的词重叠率
        curr_words = set(user_input.lower().split())
        prev_words = set(prev_input.split())
        if curr_words and prev_words:
            overlap = len(curr_words & prev_words) / max(len(curr_words), len(prev_words))
            if overlap > 0.7 and curr_words != prev_words:
                shared = curr_words & prev_words & topic_words
                if shared:
                    return STRATEGY_REPEAT.format(topic=random.choice(list(shared)))
                return STRATEGY_REPEAT.format(topic="this")

    # 5. 追问策略（本轮走兜底 + 之前提到过话题）
    # 检查是否走了兜底规则
    fallback_templates = [t for _, pat, ts in rules if pat == r'.*' for t in ts]
    if base_response in fallback_templates:
        if ctx.mentioned_topics:
            # 优先选最近没聊的话题
            topic = random.choice(list(ctx.mentioned_topics))
            return STRATEGY_FOLLOWUP.format(topic=topic)

    # 6. 话题切换（同一话题超过 5 轮）
    if len(ctx.history) >= 5 and ctx.mentioned_topics:
        recent_topics = set()
        for inp, _ in ctx.history[-5:]:
            recent_topics |= extract_topics(inp)
        if len(recent_topics) == 1:
            return STRATEGY_TOPIC_SWITCH.format(topic=list(recent_topics)[0])

    return base_response


def postprocess(response: str, rule_idx: int, ctx: ConversationContext) -> str:
    """输出后处理：填充词 + 避免重复模板 + 随机追问"""

    # 随机添加填充词（20% 概率，且不在策略回复上叠加）
    if random.random() < 0.2 and not response.startswith(("你之前", "我注意到", "你能多说", "你似乎", "我们聊了", "听起来")):
        filler = random.choice(FILLERS)
        if filler:
            response = filler + response[0].lower() + response[1:]

    # 随机追加开放式引导（15% 概率）
    if random.random() < 0.15:
        follow_up = random.choice(FOLLOW_UPS)
        if follow_up:
            response += follow_up

    return response


# ============================================================
# 8. 核心响应函数
# ============================================================
def respond(
    user_input: str,
    ctx: ConversationContext,
    enable_strategies: bool = True,
) -> str:
    """根据规则库 + 上下文 + 策略生成响应"""

    # 预处理
    cleaned, punctuation_emotion = preprocess(user_input)

    # 情感分析
    emotion = analyze_emotion(cleaned)

    # 规则匹配（按优先级遍历，同优先级选匹配最长的）
    best_match = None
    best_rule_idx = -1
    best_priority = -1
    best_match_len = 0

    for idx, (priority, pattern, _) in enumerate(rules):
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            match_len = match.end() - match.start()
            if priority > best_priority or (priority == best_priority and match_len > best_match_len):
                best_match = match
                best_rule_idx = idx
                best_priority = priority
                best_match_len = match_len

    if best_match is not None:
        _, pattern, responses = rules[best_rule_idx]
        captured_group = best_match.group(1) if best_match.groups() else ""
        swapped_group = swap_pronouns(captured_group)

        # 选择模板（避免与上次相同）
        last_idx = ctx.last_template_index.get(best_rule_idx, -1)
        available = [i for i in range(len(responses)) if i != last_idx]
        if not available:
            available = list(range(len(responses)))
        chosen_idx = random.choice(available)
        ctx.last_template_index[best_rule_idx] = chosen_idx

        base_response = responses[chosen_idx].format(swapped_group)
    else:
        # 理论上不会走到这里（兜底 r'.*' 一定匹配）
        base_response = "Please tell me more."

    # 策略层
    final_response = apply_strategies(base_response, cleaned, ctx, punctuation_emotion, enable_strategies)

    # 后处理
    final_response = postprocess(final_response, best_rule_idx, ctx)

    # 更新上下文
    ctx.add_turn(cleaned, final_response, emotion)
    ctx.last_response = final_response

    return final_response


# ============================================================
# 9. 主聊天循环
# ============================================================
SPECIAL_COMMANDS = {
    "/history": "显示对话历史",
    "/topics": "显示已提及的话题",
    "/emotion": "显示情感轨迹",
    "/help": "显示帮助信息",
}


def show_history(ctx: ConversationContext):
    if not ctx.history:
        print("  (暂无对话历史)")
        return
    for i, (user, bot) in enumerate(ctx.history, 1):
        print(f"  [{i}] You: {user}")
        print(f"       Therapist: {bot}")


def show_topics(ctx: ConversationContext):
    if not ctx.mentioned_topics:
        print("  (暂无提及话题)")
        return
    print(f"  {', '.join(sorted(ctx.mentioned_topics))}")


def show_emotion(ctx: ConversationContext):
    if not ctx.emotion_trajectory:
        print("  (暂无情感记录)")
        return
    trajectory = " → ".join(ctx.emotion_trajectory)
    print(f"  {trajectory}")


def show_help():
    print("  可用命令:")
    for cmd, desc in SPECIAL_COMMANDS.items():
        print(f"    {cmd:12s} {desc}")
    print(f"    quit/exit/bye  退出对话")
    print(f"  选项:")
    print(f"    --no-strategy  禁用策略引擎（纯规则匹配）")


if __name__ == '__main__':
    import sys

    enable_strategies = "--no-strategy" not in sys.argv

    ctx = ConversationContext()
    print("Therapist: Hello! How can I help you today?")
    print("  (输入 /help 查看可用命令)")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nTherapist: Goodbye. It was nice talking to you.")
            break

        if not user_input.strip():
            continue

        # 退出命令
        if user_input.lower().strip() in ["quit", "exit", "bye"]:
            print("Therapist: Goodbye. It was nice talking to you.")
            break

        # 特殊命令
        cmd = user_input.lower().strip()
        if cmd == "/history":
            show_history(ctx)
            continue
        if cmd == "/topics":
            show_topics(ctx)
            continue
        if cmd == "/emotion":
            show_emotion(ctx)
            continue
        if cmd == "/help":
            show_help()
            continue

        # 正常对话
        response = respond(user_input, ctx, enable_strategies=enable_strategies)
        print(f"Therapist: {response}")
