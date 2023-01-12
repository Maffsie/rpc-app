#base /feeds
#/fixers/bcb
## returns fixed rss feed for bittersweet candy bowl
## js: msg.payload=msg.payload.replace(/&rsquo;/g,'&amp;rsquo;');

#/macalope
## returns rss feed for the macalope
## get https://www.macworld.com/feed
## transform from xml
## payload.rss.channel[0].title[0] set to The Macalope
## payload.rss.channel[0].link[0] set to https://api.puppy.network/feeds/macalope
## payload.rss.channel[0].atom:link[0] removed
## js: var items=msg.payload.rss.channel[0].item
###      .filter(item => item["dc:creator"][0].includes("Macalope"));
###    msg.payload.rss.channel[0].item=items;
## re-transform to xml
## return