/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import java.net.URL;
import java.util.List;
import org.jdom.Document;
import valerie.MediaInfo;

/**
 *
 * @author Admin
 */
public class theTvDb extends provider {

    public void getDataById(MediaInfo info) {
        if(info.isSeries)
            getSeriesById(info);
    }

    public void getArtById(MediaInfo info) {
        if(info.isSeries)
            getSeriesArtById(info);
    }

    public void getDataByTitle(MediaInfo info) {
        if(info.isSeries) {
            getSeriesByTitle(info);
            getSeriesById(info);
        }
        else if(info.isEpisode)
            getEpisode(info);
    }

    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    //////////////////////////////////////////////////

    private String APIKEY = "3A042860EF9F9160";
    private String apiSearch = "http://www.thetvdb.com/api/GetSeries.php?seriesname=";
    private String apiSearchEpisode = "http://www.thetvdb.com/api/" + APIKEY + "/series/<seriesid>/default/<season>/<episode>/7.xml";
    private String apiArt = "http://www.thetvdb.com/banners/";
    private String apiSeriesByID = "http://www.thetvdb.com/data/series/<seriesid>/";

    private void getSeriesById(MediaInfo info) {
       Document xml = null;
       try {
           String url = apiSeriesByID.replaceAll("<seriesid>", String.valueOf( info.TheTvDb));
               xml = new valerie.tools.webgrabber().getXML(new URL(url));
       } catch (Exception ex) {}

       if (xml == null)
            return;

       List movieList = xml.getRootElement().getChildren("Series");
       for(int i = 0; i < movieList.size(); i++)
       {
           org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

           int Year = 0;
           org.jdom.Element eYear = eMovie.getChild("FirstAired");
           if(eYear != null)
                Year = Integer.parseInt(eYear.getText().substring(0, eYear.getText().indexOf("-")));

           info.Year = Year;

           org.jdom.Element ePlot = eMovie.getChild("Overview");
           if(ePlot != null)
                info.Plot = ePlot.getText();

           org.jdom.Element eImdb = eMovie.getChild("IMDB_ID");
           if(eImdb != null && eImdb.getText().length() > 3)
                info.Imdb = Integer.valueOf(eImdb.getText().substring(2));

           org.jdom.Element eTitle = eMovie.getChild("SeriesName");
           if(eTitle != null)
                info.Title = eTitle.getText();

           org.jdom.Element eRating = eMovie.getChild("Rating");
           if(eRating != null && eRating.getText().length() > 0) {
                String sPopularity = eRating.getText();
                System.out.println(sPopularity);
                Float fPopularity = Float.valueOf(sPopularity);
                info.Popularity = fPopularity.intValue();
           }

           org.jdom.Element eGenres = eMovie.getChild("Genre");
           if(eGenres != null)
                info.Genres = eGenres.getText();

           if (info.Year <= 1980)
               continue;

           break;
       }
        return;
    }

    private void getSeriesByTitle(MediaInfo info) {
       Document xml = null;
       try {
           String urlTitle = info.SearchString;
           urlTitle = urlTitle.replaceAll(" ", "+");
           xml = new valerie.tools.webgrabber().getXML(new URL(apiSearch + urlTitle));
       } catch (Exception ex) {}

       if (xml == null)
            return;

       List movieList = xml.getRootElement().getChildren("Series");
       for(int i = 0; i < movieList.size(); i++)
       {
           org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

           int Year = 0;
           org.jdom.Element eYear = eMovie.getChild("FirstAired");
           if(eYear != null)
                Year = Integer.parseInt(eYear.getText().substring(0, eYear.getText().indexOf("-")));

           info.Year = Year;

           org.jdom.Element ePlot = eMovie.getChild("Overview");
           if(ePlot != null)
                info.Plot = ePlot.getText();

           org.jdom.Element eImdb = eMovie.getChild("IMDB_ID");
           if(eImdb != null)
                info.Imdb = Integer.valueOf(eImdb.getText().substring(2));

           org.jdom.Element eID = eMovie.getChild("id");
           if(eID != null)
                 info.TheTvDb = Integer.valueOf(eID.getText());

           org.jdom.Element eTitle = eMovie.getChild("SeriesName");
           if(eTitle != null)
                info.Title = eTitle.getText();

           if (info.Year <= 1980)
               continue;

           break;
       }
        return;
    }

    private void getEpisode(MediaInfo info) {

        if( info.TheTvDb == 0)
            return;

           Document xml = null;
           try {
               String url = apiSearchEpisode.replaceAll("<seriesid>", String.valueOf( info.TheTvDb));
               url = url.replaceAll("<season>", String.valueOf(info.Season));
               url = url.replaceAll("<episode>", String.valueOf(info.Episode));
               xml = new valerie.tools.webgrabber().getXML(new URL(url));
           } catch (Exception ex) {}

           if (xml == null)
                return;

           List movieList = xml.getRootElement().getChildren("Episode");
           for(int i = 0; i < movieList.size(); i++)
           {
               org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

               org.jdom.Element ePlot = eMovie.getChild("Overview");
               if(ePlot != null)
                    info.Plot = ePlot.getText();

               org.jdom.Element eImdb = eMovie.getChild("IMDB_ID");
               if(eImdb != null && eImdb.getText().length() > 2)
                    info.Imdb = Integer.valueOf(eImdb.getText().substring(2));

               /*org.jdom.Element eID = eMovie.getChild("id");
               if(eID != null)
                    episodesID = Integer.valueOf(eID.getText());*/

               org.jdom.Element eTitle = eMovie.getChild("EpisodeName");
               if(eTitle != null)
                    info.Title = eTitle.getText();

               break;
           }
            return;
        }

    private void getSeriesArtById(MediaInfo info) {
       Document xml = null;
       try {
           String url = apiSeriesByID.replaceAll("<seriesid>", String.valueOf( info.TheTvDb));
               xml = new valerie.tools.webgrabber().getXML(new URL(url));
       } catch (Exception ex) {}

       if (xml == null)
            return;

       List movieList = xml.getRootElement().getChildren("Series");
       for(int i = 0; i < movieList.size(); i++)
       {
           org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

           org.jdom.Element eBanner = eMovie.getChild("banner");
           if(eBanner != null && eBanner.getText().length() > 0)
                info.Banner = apiArt + eBanner.getText();

           org.jdom.Element ePoster = eMovie.getChild("poster");
           if(ePoster != null && ePoster.getText().length() > 0)
                info.Poster = apiArt + ePoster.getText();

           org.jdom.Element eFanart = eMovie.getChild("fanart");
           if(eFanart != null && eFanart.getText().length() > 0)
                info.Backdrop = apiArt + eFanart.getText();

           break;
       }
        return;
    }
}
