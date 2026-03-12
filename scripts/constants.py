# -*- coding: utf-8 -*-
"""全局常量、分类元数据与 RSS 源列表。"""

from typing import Dict
from typing import List
from typing import Literal

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemini-2.0-flash:generateContent"
)
OPENAI_DEFAULT_API_BASE = "https://api.openai.com/v1"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
FEED_FETCH_TIMEOUT_S = 15
FEED_CONCURRENCY = 10
AI_BATCH_SIZE = 10
MAX_CONCURRENT_AI = 2

CategoryId = Literal[
    "ai-ml",
    "security",
    "engineering",
    "tools",
    "opinion",
    "other",
]

VALID_CATEGORIES: set[str] = {
    "ai-ml",
    "security",
    "engineering",
    "tools",
    "opinion",
    "other",
}

CATEGORY_META: Dict[str, Dict[str, str]] = {
    "ai-ml": {"emoji": "🤖", "label": "AI / ML"},
    "security": {"emoji": "🔒", "label": "安全"},
    "engineering": {"emoji": "⚙️", "label": "工程"},
    "tools": {"emoji": "🛠", "label": "工具 / 开源"},
    "opinion": {"emoji": "💡", "label": "观点 / 杂谈"},
    "other": {"emoji": "📝", "label": "其他"},
}

# 90 RSS feeds from Hacker News Popularity Contest 2025
RSS_FEEDS: List[Dict[str, str]] = [
    {"name": "simonwillison.net", "xml_url": "https://simonwillison.net/atom/everything/", "html_url": "https://simonwillison.net"},
    {"name": "jeffgeerling.com", "xml_url": "https://www.jeffgeerling.com/blog.xml", "html_url": "https://jeffgeerling.com"},
    {"name": "seangoedecke.com", "xml_url": "https://www.seangoedecke.com/rss.xml", "html_url": "https://seangoedecke.com"},
    {"name": "krebsonsecurity.com", "xml_url": "https://krebsonsecurity.com/feed/", "html_url": "https://krebsonsecurity.com"},
    {"name": "daringfireball.net", "xml_url": "https://daringfireball.net/feeds/main", "html_url": "https://daringfireball.net"},
    {"name": "ericmigi.com", "xml_url": "https://ericmigi.com/rss.xml", "html_url": "https://ericmigi.com"},
    {"name": "antirez.com", "xml_url": "http://antirez.com/rss", "html_url": "http://antirez.com"},
    {"name": "idiallo.com", "xml_url": "https://idiallo.com/feed.rss", "html_url": "https://idiallo.com"},
    {"name": "maurycyz.com", "xml_url": "https://maurycyz.com/index.xml", "html_url": "https://maurycyz.com"},
    {"name": "pluralistic.net", "xml_url": "https://pluralistic.net/feed/", "html_url": "https://pluralistic.net"},
    {"name": "shkspr.mobi", "xml_url": "https://shkspr.mobi/blog/feed/", "html_url": "https://shkspr.mobi"},
    {"name": "lcamtuf.substack.com", "xml_url": "https://lcamtuf.substack.com/feed", "html_url": "https://lcamtuf.substack.com"},
    {"name": "mitchellh.com", "xml_url": "https://mitchellh.com/feed.xml", "html_url": "https://mitchellh.com"},
    {"name": "dynomight.net", "xml_url": "https://dynomight.net/feed.xml", "html_url": "https://dynomight.net"},
    {"name": "utcc.utoronto.ca/~cks", "xml_url": "https://utcc.utoronto.ca/~cks/space/blog/?atom", "html_url": "https://utcc.utoronto.ca/~cks"},
    {"name": "xeiaso.net", "xml_url": "https://xeiaso.net/blog.rss", "html_url": "https://xeiaso.net"},
    {"name": "devblogs.microsoft.com/oldnewthing", "xml_url": "https://devblogs.microsoft.com/oldnewthing/feed", "html_url": "https://devblogs.microsoft.com/oldnewthing"},
    {"name": "righto.com", "xml_url": "https://www.righto.com/feeds/posts/default", "html_url": "https://righto.com"},
    {"name": "lucumr.pocoo.org", "xml_url": "https://lucumr.pocoo.org/feed.atom", "html_url": "https://lucumr.pocoo.org"},
    {"name": "skyfall.dev", "xml_url": "https://skyfall.dev/rss.xml", "html_url": "https://skyfall.dev"},
    {"name": "garymarcus.substack.com", "xml_url": "https://garymarcus.substack.com/feed", "html_url": "https://garymarcus.substack.com"},
    {"name": "rachelbythebay.com", "xml_url": "https://rachelbythebay.com/w/atom.xml", "html_url": "https://rachelbythebay.com"},
    {"name": "overreacted.io", "xml_url": "https://overreacted.io/rss.xml", "html_url": "https://overreacted.io"},
    {"name": "timsh.org", "xml_url": "https://timsh.org/rss/", "html_url": "https://timsh.org"},
    {"name": "johndcook.com", "xml_url": "https://www.johndcook.com/blog/feed/", "html_url": "https://johndcook.com"},
    {"name": "gilesthomas.com", "xml_url": "https://gilesthomas.com/feed/rss.xml", "html_url": "https://gilesthomas.com"},
    {"name": "matklad.github.io", "xml_url": "https://matklad.github.io/feed.xml", "html_url": "https://matklad.github.io"},
    {"name": "derekthompson.org", "xml_url": "https://www.theatlantic.com/feed/author/derek-thompson/", "html_url": "https://derekthompson.org"},
    {"name": "evanhahn.com", "xml_url": "https://evanhahn.com/feed.xml", "html_url": "https://evanhahn.com"},
    {"name": "terriblesoftware.org", "xml_url": "https://terriblesoftware.org/feed/", "html_url": "https://terriblesoftware.org"},
    {"name": "rakhim.exotext.com", "xml_url": "https://rakhim.exotext.com/rss.xml", "html_url": "https://rakhim.exotext.com"},
    {"name": "joanwestenberg.com", "xml_url": "https://joanwestenberg.com/rss", "html_url": "https://joanwestenberg.com"},
    {"name": "xania.org", "xml_url": "https://xania.org/feed", "html_url": "https://xania.org"},
    {"name": "micahflee.com", "xml_url": "https://micahflee.com/feed/", "html_url": "https://micahflee.com"},
    {"name": "nesbitt.io", "xml_url": "https://nesbitt.io/feed.xml", "html_url": "https://nesbitt.io"},
    {"name": "construction-physics.com", "xml_url": "https://www.construction-physics.com/feed", "html_url": "https://construction-physics.com"},
    {"name": "tedium.co", "xml_url": "https://feed.tedium.co/", "html_url": "https://tedium.co"},
    {"name": "susam.net", "xml_url": "https://susam.net/feed.xml", "html_url": "https://susam.net"},
    {"name": "entropicthoughts.com", "xml_url": "https://entropicthoughts.com/feed.xml", "html_url": "https://entropicthoughts.com"},
    {"name": "buttondown.com/hillelwayne", "xml_url": "https://buttondown.com/hillelwayne/rss", "html_url": "https://buttondown.com/hillelwayne"},
    {"name": "dwarkesh.com", "xml_url": "https://www.dwarkeshpatel.com/feed", "html_url": "https://dwarkesh.com"},
    {"name": "borretti.me", "xml_url": "https://borretti.me/feed.xml", "html_url": "https://borretti.me"},
    {"name": "wheresyoured.at", "xml_url": "https://www.wheresyoured.at/rss/", "html_url": "https://wheresyoured.at"},
    {"name": "jayd.ml", "xml_url": "https://jayd.ml/feed.xml", "html_url": "https://jayd.ml"},
    {"name": "minimaxir.com", "xml_url": "https://minimaxir.com/index.xml", "html_url": "https://minimaxir.com"},
    {"name": "geohot.github.io", "xml_url": "https://geohot.github.io/blog/feed.xml", "html_url": "https://geohot.github.io"},
    {"name": "paulgraham.com", "xml_url": "http://www.aaronsw.com/2002/feeds/pgessays.rss", "html_url": "https://paulgraham.com"},
    {"name": "filfre.net", "xml_url": "https://www.filfre.net/feed/", "html_url": "https://filfre.net"},
    {"name": "blog.jim-nielsen.com", "xml_url": "https://blog.jim-nielsen.com/feed.xml", "html_url": "https://blog.jim-nielsen.com"},
    {"name": "dfarq.homeip.net", "xml_url": "https://dfarq.homeip.net/feed/", "html_url": "https://dfarq.homeip.net"},
    {"name": "jyn.dev", "xml_url": "https://jyn.dev/atom.xml", "html_url": "https://jyn.dev"},
    {"name": "geoffreylitt.com", "xml_url": "https://www.geoffreylitt.com/feed.xml", "html_url": "https://geoffreylitt.com"},
    {"name": "downtowndougbrown.com", "xml_url": "https://www.downtowndougbrown.com/feed/", "html_url": "https://downtowndougbrown.com"},
    {"name": "brutecat.com", "xml_url": "https://brutecat.com/rss.xml", "html_url": "https://brutecat.com"},
    {"name": "eli.thegreenplace.net", "xml_url": "https://eli.thegreenplace.net/feeds/all.atom.xml", "html_url": "https://eli.thegreenplace.net"},
    {"name": "abortretry.fail", "xml_url": "https://www.abortretry.fail/feed", "html_url": "https://abortretry.fail"},
    {"name": "fabiensanglard.net", "xml_url": "https://fabiensanglard.net/rss.xml", "html_url": "https://fabiensanglard.net"},
    {"name": "oldvcr.blogspot.com", "xml_url": "https://oldvcr.blogspot.com/feeds/posts/default", "html_url": "https://oldvcr.blogspot.com"},
    {"name": "bogdanthegeek.github.io", "xml_url": "https://bogdanthegeek.github.io/blog/index.xml", "html_url": "https://bogdanthegeek.github.io"},
    {"name": "hugotunius.se", "xml_url": "https://hugotunius.se/feed.xml", "html_url": "https://hugotunius.se"},
    {"name": "gwern.net", "xml_url": "https://gwern.substack.com/feed", "html_url": "https://gwern.net"},
    {"name": "berthub.eu", "xml_url": "https://berthub.eu/articles/index.xml", "html_url": "https://berthub.eu"},
    {"name": "chadnauseam.com", "xml_url": "https://chadnauseam.com/rss.xml", "html_url": "https://chadnauseam.com"},
    {"name": "simone.org", "xml_url": "https://simone.org/feed/", "html_url": "https://simone.org"},
    {"name": "it-notes.dragas.net", "xml_url": "https://it-notes.dragas.net/feed/", "html_url": "https://it-notes.dragas.net"},
    {"name": "beej.us", "xml_url": "https://beej.us/blog/rss.xml", "html_url": "https://beej.us"},
    {"name": "hey.paris", "xml_url": "https://hey.paris/index.xml", "html_url": "https://hey.paris"},
    {"name": "danielwirtz.com", "xml_url": "https://danielwirtz.com/rss.xml", "html_url": "https://danielwirtz.com"},
    {"name": "matduggan.com", "xml_url": "https://matduggan.com/rss/", "html_url": "https://matduggan.com"},
    {"name": "refactoringenglish.com", "xml_url": "https://refactoringenglish.com/index.xml", "html_url": "https://refactoringenglish.com"},
    {"name": "worksonmymachine.substack.com", "xml_url": "https://worksonmymachine.substack.com/feed", "html_url": "https://worksonmymachine.substack.com"},
    {"name": "philiplaine.com", "xml_url": "https://philiplaine.com/index.xml", "html_url": "https://philiplaine.com"},
    {"name": "steveblank.com", "xml_url": "https://steveblank.com/feed/", "html_url": "https://steveblank.com"},
    {"name": "bernsteinbear.com", "xml_url": "https://bernsteinbear.com/feed.xml", "html_url": "https://bernsteinbear.com"},
    {"name": "danieldelaney.net", "xml_url": "https://danieldelaney.net/feed", "html_url": "https://danieldelaney.net"},
    {"name": "troyhunt.com", "xml_url": "https://www.troyhunt.com/rss/", "html_url": "https://troyhunt.com"},
    {"name": "herman.bearblog.dev", "xml_url": "https://herman.bearblog.dev/feed/", "html_url": "https://herman.bearblog.dev"},
    {"name": "tomrenner.com", "xml_url": "https://tomrenner.com/index.xml", "html_url": "https://tomrenner.com"},
    {"name": "blog.pixelmelt.dev", "xml_url": "https://blog.pixelmelt.dev/rss/", "html_url": "https://blog.pixelmelt.dev"},
    {"name": "martinalderson.com", "xml_url": "https://martinalderson.com/feed.xml", "html_url": "https://martinalderson.com"},
    {"name": "danielchasehooper.com", "xml_url": "https://danielchasehooper.com/feed.xml", "html_url": "https://danielchasehooper.com"},
    {"name": "chiark.greenend.org.uk/~sgtatham", "xml_url": "https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/feed.xml", "html_url": "https://chiark.greenend.org.uk/~sgtatham"},
    {"name": "grantslatton.com", "xml_url": "https://grantslatton.com/rss.xml", "html_url": "https://grantslatton.com"},
    {"name": "experimental-history.com", "xml_url": "https://www.experimental-history.com/feed", "html_url": "https://experimental-history.com"},
    {"name": "anildash.com", "xml_url": "https://anildash.com/feed.xml", "html_url": "https://anildash.com"},
    {"name": "aresluna.org", "xml_url": "https://aresluna.org/main.rss", "html_url": "https://aresluna.org"},
    {"name": "michael.stapelberg.ch", "xml_url": "https://michael.stapelberg.ch/feed.xml", "html_url": "https://michael.stapelberg.ch"},
    {"name": "miguelgrinberg.com", "xml_url": "https://blog.miguelgrinberg.com/feed", "html_url": "https://miguelgrinberg.com"},
    {"name": "keygen.sh", "xml_url": "https://keygen.sh/blog/feed.xml", "html_url": "https://keygen.sh"},
    {"name": "mjg59.dreamwidth.org", "xml_url": "https://mjg59.dreamwidth.org/data/rss", "html_url": "https://mjg59.dreamwidth.org"},
    {"name": "computer.rip", "xml_url": "https://computer.rip/rss.xml", "html_url": "https://computer.rip"},
    {"name": "tedunangst.com", "xml_url": "https://www.tedunangst.com/flak/rss", "html_url": "https://tedunangst.com"},
]
