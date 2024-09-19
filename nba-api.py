import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import commonplayerinfo, shotchartdetail, teamyearbyyearstats, playercareerstats, leaguedashteamstats, leaguedashplayerstats, commonteamroster, playergamelog


NBA_TEAM_LOGOS = {
    "Atlanta Hawks": "https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg",
    "Boston Celtics": "https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg",
    "Brooklyn Nets": "https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg",
    "Charlotte Hornets": "https://cdn.nba.com/logos/nba/1610612766/primary/L/logo.svg",
    "Chicago Bulls": "https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg",
    "Cleveland Cavaliers": "https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg",
    "Dallas Mavericks": "https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg",
    "Denver Nuggets": "https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg",
    "Detroit Pistons": "https://cdn.nba.com/logos/nba/1610612765/primary/L/logo.svg",
    "Golden State Warriors": "https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg",
    "Houston Rockets": "https://cdn.nba.com/logos/nba/1610612745/primary/L/logo.svg",
    "Indiana Pacers": "https://cdn.nba.com/logos/nba/1610612754/primary/L/logo.svg",
    "LA Clippers": "https://cdn.nba.com/logos/nba/1610612746/primary/L/logo.svg",
    "Los Angeles Lakers": "https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg",
    "Memphis Grizzlies": "https://cdn.nba.com/logos/nba/1610612763/primary/L/logo.svg",
    "Miami Heat": "https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg",
    "Milwaukee Bucks": "https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg",
    "Minnesota Timberwolves": "https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg",
    "New Orleans Pelicans": "https://cdn.nba.com/logos/nba/1610612740/primary/L/logo.svg",
    "New York Knicks": "https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg",
    "Oklahoma City Thunder": "https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg",
    "Orlando Magic": "https://cdn.nba.com/logos/nba/1610612753/primary/L/logo.svg",
    "Philadelphia 76ers": "https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg",
    "Phoenix Suns": "https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg",
    "Portland Trail Blazers": "https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg",
    "Sacramento Kings": "https://cdn.nba.com/logos/nba/1610612758/primary/L/logo.svg",
    "San Antonio Spurs": "https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg",
    "Toronto Raptors": "https://cdn.nba.com/logos/nba/1610612761/primary/L/logo.svg",
    "Utah Jazz": "https://cdn.nba.com/logos/nba/1610612762/primary/L/logo.svg",
    "Washington Wizards": "https://cdn.nba.com/logos/nba/1610612764/primary/L/logo.svg"
}


def get_team_starting_five(team_id, season):
    roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season).get_data_frames()[0]
    
    # Mevcut sütunları kontrol et
    if 'GP' in roster.columns:
        starting_five = roster.sort_values('GP', ascending=False).head(5)
    elif 'PLAYER_ID' in roster.columns:
        # Eğer GP yoksa, varsayılan olarak PLAYER_ID'ye göre sırala
        starting_five = roster.sort_values('PLAYER_ID').head(5)
    else:
        # Eğer hiçbiri yoksa, ilk 5 satırı al
        starting_five = roster.head(5)
    
    return starting_five

def create_court(fig, fig_width=1000, margins=10):
    # Basketbol sahası çizgilerini oluştur
    outer_lines_color = "#000000"
    inner_lines_color = "#000000"
    
    # Dış sınırlar
    fig.add_shape(type="rect", x0=-250, y0=-47.5, x1=250, y1=422.5, line=dict(color=outer_lines_color, width=2))
    
    # Üç sayı çizgisi
    fig.add_shape(type="line", x0=-220, y0=-47.5, x1=-220, y1=140, line=dict(color=inner_lines_color, width=2))
    fig.add_shape(type="line", x0=220, y0=-47.5, x1=220, y1=140, line=dict(color=inner_lines_color, width=2))
    fig.add_shape(type="path", path="M -220 140 Q 0 190 220 140", line=dict(color=inner_lines_color, width=2))
    
    # Serbest atış çemberi
    fig.add_shape(type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, line=dict(color=inner_lines_color, width=2))
    
    # Serbest atış yarım dairesi
    fig.add_shape(type="path", path="M -60 77.5 Q 0 57.5 60 77.5", line=dict(color=inner_lines_color, width=2))
    
    # Pota
    fig.add_shape(type="rect", x0=-15, y0=-7.5, x1=15, y1=-12.5, line=dict(color="#000000", width=2), fillcolor="#000000")
    
    # Çember
    fig.add_shape(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, line=dict(color="#ff0000", width=3))
    
    # Restricted area
    fig.add_shape(type="path", path="M -80 -47.5 Q 0 -17.5 80 -47.5", line=dict(color=inner_lines_color, width=2))
    
    # Saha düzenlemesi
    fig.update_xaxes(range=[-250, 250], showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(range=[-47.5, 422.5], showgrid=False, zeroline=False, visible=False)
    
    fig.update_layout(
        width=fig_width,
        height=fig_width*94/50,
        margin=dict(l=margins, r=margins, t=margins, b=margins),
        plot_bgcolor='rgba(255,255,255,0.8)',
        paper_bgcolor='rgba(255,255,255,0.8)'
    )
    
    return fig

def filter_players(search):
    all_players = players.get_players()
    return [player['full_name'] for player in all_players if search.lower() in player['full_name'].lower()]

def filter_players_by_team(team_id):
    team_players = commonteamroster.CommonTeamRoster(team_id=team_id).get_data_frames()[0]
    return team_players['PLAYER'].tolist()

def get_league_averages(season):
    league_stats = leaguedashteamstats.LeagueDashTeamStats(season=season, per_mode_detailed="PerGame").get_data_frames()[0]
    return league_stats[['PTS', 'AST', 'REB', 'STL', 'BLK']].mean()

def get_player_league_averages(season):
    league_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed="PerGame").get_data_frames()[0]
    return league_stats[['PTS', 'AST', 'REB', 'STL', 'BLK']].mean()

def get_player_season_stats(player_id, season):
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    season_stats = game_log[['PTS', 'AST', 'REB', 'STL', 'BLK']].mean()
    return season_stats

def display_team_info(team_name):
    team_dict = [team for team in teams.get_teams() if team['full_name'] == team_name][0]
    team_id = team_dict['id']
    
    st.subheader(f"{team_name} Information")
    st.write(f"Nickname: {team_dict['nickname']}")
    st.write(f"City: {team_dict['city']}")
    st.write(f"State: {team_dict['state']}")
    st.write(f"Year Founded: {team_dict['year_founded']}")
    
    team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id).get_data_frames()[0]

    team_stats = team_stats[team_stats['YEAR'] >= '1996-97']
    
    # Sezon seçimi için bir selectbox ekleyelim
    seasons = team_stats['YEAR'].unique()
    selected_season = st.selectbox("Select a season:", seasons, index=len(seasons)-1)
    
    # Seçilen sezona göre istatistikleri filtreleyelim
    season_stats = team_stats[team_stats['YEAR'] == selected_season].iloc[0]
    
    st.subheader(f"Statistics for {selected_season} Season")
    st.write(f"Wins: {season_stats['WINS']}")
    st.write(f"Losses: {season_stats['LOSSES']}")
    st.write(f"Win Percentage: {season_stats['WIN_PCT']:.3f}")
    st.write(f"Points Per Game: {season_stats['PTS'] / season_stats['GP']:.1f}")
    st.write(f"Assists Per Game: {season_stats['AST'] / season_stats['GP']:.1f}")
    st.write(f"Rebounds Per Game: {season_stats['REB'] / season_stats['GP']:.1f}")

    try:
        league_avg = get_league_averages(selected_season)
        
        stats = ['PTS', 'AST', 'REB', 'STL', 'BLK']
        team_values = [float(season_stats[stat]) / float(season_stats['GP']) for stat in stats]
        league_values = [float(league_avg[stat]) for stat in stats]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=stats, y=team_values, name=team_name, marker_color='#007bff'))  # Mavi
        fig.add_trace(go.Bar(x=stats, y=league_values, name='League Average', marker_color='#dc3545'))  # Kırmızı
        fig.update_layout(
            title=f'{team_name} vs League Average ({selected_season})',
            barmode='group',
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(color='#333333')
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"An error occurred while creating the comparison chart: {str(e)}")

    # İlk beşi ve istatistiklerini göster
    st.subheader(f"Starting Five for {selected_season} Season")
    starting_five = get_team_starting_five(team_id, selected_season)
    
    for _, player in starting_five.iterrows():
        player_name = player['PLAYER']
        player_id = player['PLAYER_ID']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{player_name}** ({player.get('POSITION', 'N/A')})")
        
        with col2:
            try:
                player_stats = get_player_season_stats(player_id, selected_season)
                st.write(f"PPG: {player_stats['PTS']:.1f}, APG: {player_stats['AST']:.1f}, RPG: {player_stats['REB']:.1f}")
            except Exception as e:
                st.write(f"Stats not available: {str(e)}")

def display_player_info(player_name):
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        player = player_dict[0]
        player_id = player['id']
        
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
        
        st.subheader(f"{player_name} Information")
        st.write(f"Team: {player_info['TEAM_NAME'].iloc[0]}")
        st.write(f"Position: {player_info['POSITION'].iloc[0]}")
        st.write(f"Height: {player_info['HEIGHT'].iloc[0]}")
        st.write(f"Weight: {player_info['WEIGHT'].iloc[0]}")
        
        # Oyuncunun kariyer istatistiklerini alalım
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
        
        # Sezon seçimi için bir selectbox ekleyelim
        seasons = career_stats['SEASON_ID'].unique()
        seasons = [season for season in seasons if season != 'CAREER']
        selected_season = st.selectbox("Select a season:", seasons, index=len(seasons)-1)
        
        # Seçilen sezona göre istatistikleri filtreleyelim
        season_stats = career_stats[career_stats['SEASON_ID'] == selected_season].iloc[0]
        
        st.subheader(f"Statistics for {selected_season} Season")
        st.write(f"Games Played: {season_stats['GP']}")
        st.write(f"Points Per Game: {season_stats['PTS'] / season_stats['GP']:.1f}")
        st.write(f"Assists Per Game: {season_stats['AST'] / season_stats['GP']:.1f}")
        st.write(f"Rebounds Per Game: {season_stats['REB'] / season_stats['GP']:.1f}")
        st.write(f"Steals Per Game: {season_stats['STL'] / season_stats['GP']:.1f}")
        st.write(f"Blocks Per Game: {season_stats['BLK'] / season_stats['GP']:.1f}")
        
        try:
            # Seçilen sezona göre lig ortalamalarını alalım
            league_avg = get_player_league_averages(selected_season)
            
            stats = ['PTS', 'AST', 'REB', 'STL', 'BLK']
            player_values = [float(season_stats[stat]) / float(season_stats['GP']) for stat in stats]
            league_values = [float(league_avg[stat]) for stat in stats]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=stats, y=player_values, name=f"{player_name}", marker_color='#007bff'))
            fig.add_trace(go.Bar(x=stats, y=league_values, name=f'League Average', marker_color='#dc3545'))
            fig.update_layout(title=f'{player_name} vs League Average ({selected_season})', barmode='group')
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"An error occurred while creating the comparison chart: {str(e)}")
        
        # Şut haritası
        shot_chart = shotchartdetail.ShotChartDetail(player_id=player_id, team_id=0, season_nullable=selected_season, context_measure_simple="FGA").get_data_frames()[0]
    
        fig = go.Figure()
    
    # Basketbol sahasını oluştur
        fig = create_court(fig, fig_width=600, margins=0)
    
    # Şutları ekle
        made_shots = shot_chart[shot_chart.SHOT_MADE_FLAG == 1]
        missed_shots = shot_chart[shot_chart.SHOT_MADE_FLAG == 0]
    
        fig.add_trace(go.Scatter(
            x=made_shots.LOC_X,
            y=made_shots.LOC_Y,
            mode='markers',
            marker=dict(
                size=7,
                color='green',
                symbol='circle',
                line=dict(width=1, color='black')
            ),
            name='Made Shot',
            hoverinfo='text',
            text=[f'Made from {shot.SHOT_ZONE_BASIC}' for _, shot in made_shots.iterrows()]
        ))
    
        fig.add_trace(go.Scatter(
            x=missed_shots.LOC_X,
            y=missed_shots.LOC_Y,
            mode='markers',
            marker=dict(
                size=7,
                color='red',
                symbol='x',
                line=dict(width=1, color='black')
            ),
            name='Missed Shot',
            hoverinfo='text',
            text=[f'Missed from {shot.SHOT_ZONE_BASIC}' for _, shot in missed_shots.iterrows()]
        ))
    
        fig.update_layout(
            title=dict(
                text=f"{player_name} Shot Chart ({selected_season})",
                y=0.99,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=20)
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
        st.plotly_chart(fig, use_container_width=True)

def display_league_leaders():
    # Oyuncu liderleri
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2022-23", per_mode_detailed="PerGame").get_data_frames()[0]
    
    # Sayı liderleri
    points_leaders = player_stats.nlargest(5, 'PTS')[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS']]
    points_leaders.columns = ['Player', 'Team', 'Points']
    points_leaders.index = range(1, 6)
    points_leaders = points_leaders.reset_index().rename(columns={'index': 'Rank'})
    st.subheader("Points Leaders")
    st.dataframe(points_leaders.style.set_properties(**{'color': '#333333', 'font-weight': '400'}))

    # Asist liderleri
    assists_leaders = player_stats.nlargest(5, 'AST')[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'AST']]
    assists_leaders.columns = ['Player', 'Team', 'Assists']
    assists_leaders.index = range(1, 6)
    assists_leaders = assists_leaders.reset_index().rename(columns={'index': 'Rank'})
    st.subheader("Assists Leaders")
    st.dataframe(assists_leaders.style.set_properties(**{'color': '#333333', 'font-weight': '400'}))

    # Ribaund liderleri
    rebounds_leaders = player_stats.nlargest(5, 'REB')[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'REB']]
    rebounds_leaders.columns = ['Player', 'Team', 'Rebounds']
    rebounds_leaders.index = range(1, 6)
    rebounds_leaders = rebounds_leaders.reset_index().rename(columns={'index': 'Rank'})
    st.subheader("Rebounds Leaders")
    st.dataframe(rebounds_leaders.style.set_properties(**{'color': '#333333', 'font-weight': '400'}))

    # Takım liderleri
    team_stats = leaguedashteamstats.LeagueDashTeamStats(season="2022-23").get_data_frames()[0]
    
    # Galibiyet liderleri
    wins_leaders = team_stats.nlargest(5, 'W')[['TEAM_NAME', 'W']]
    wins_leaders.columns = ['Team', 'Wins']
    wins_leaders.index = range(1, 6)
    wins_leaders = wins_leaders.reset_index().rename(columns={'index': 'Rank'})
    st.subheader("Wins Leaders")
    st.dataframe(wins_leaders.style.set_properties(**{'color': '#333333', 'font-weight': '400'}))

def main():
    st.set_page_config(page_title="NBA Stats", page_icon="🏀", layout="wide")

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    st.title("NBA Data Viewer")

    option = st.selectbox("Select an option:", ["League Leaders", "Team", "Player"])

    if option == "League Leaders":
        display_league_leaders()
    elif option == "Team":
        team_names = [team['full_name'] for team in teams.get_teams()]
        selected_team = st.selectbox("Select a team:", team_names)
        
        # Logo ve takım adını yan yana göster
        col1, col2 = st.columns([1, 4])
        with col1:
            logo_url = NBA_TEAM_LOGOS.get(selected_team, "https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg")
            st.image(logo_url, width=100, use_column_width=True)
        with col2:
            st.markdown(f"<h2 style='margin-top: 15px;'>{selected_team}</h2>", unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)  # Yatay çizgi ekle
        display_team_info(selected_team)
    elif option == "Player":
        player_names = filter_players("")
        selected_player = st.selectbox("Select or type a player name:", player_names)
        display_player_info(selected_player)

if __name__ == "__main__":
    main()
