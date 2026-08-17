import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { getSortedPosts } from "@/utils/getSortedPosts";
import { getPostUrl } from "@/utils/getPostPaths";
import { getDescription } from "@/utils/getDescription";
import config from "@/config";

export async function GET() {
  const posts = await getCollection("posts");
  const sortedPosts = getSortedPosts(posts);

  return rss({
    title: config.site.title,
    description: config.site.description,
    site: config.site.url,
    items: sortedPosts.map(post => ({
      link: getPostUrl(post, config.site.lang),
      title: post.data.title,
      description: getDescription(post),
      // pubDate is the PUBLISH date. Feeding it `lastmod` re-dates a post every
      // time it is touched, and most readers treat a changed pubDate as a new
      // item -- editing one old post would resurface it in every subscriber's
      // timeline.
      pubDate: new Date(post.data.date),
    })),
  });
}
