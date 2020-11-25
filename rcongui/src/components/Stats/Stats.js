import React from "react";
import moment from 'moment'
import { fromJS, List as iList } from "immutable";
import Canvas from "react-canvas-js";
import {
  postData,
  showResponse,
  get,
  handle_http_errors,
} from "../../utils/fetchUtils";
import Grid from "@material-ui/core/Grid";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import Avatar from "@material-ui/core/Avatar";
import ImageIcon from "@material-ui/icons/Image";
import WorkIcon from "@material-ui/icons/Work";
import BeachAccessIcon from "@material-ui/icons/BeachAccess";

const MapList = ({ mapList, classes }) => {
  return (
    <List className={classes.root}>
      {mapList.map((m) => (
        <ListItem>
          <ListItemAvatar>
            <Avatar>
              <ImageIcon />
            </Avatar>
          </ListItemAvatar>
          <ListItemText primary={m.get("long_name")} secondary={m.get("start_timestamp")} />
        </ListItem>
      ))}
    </List>
  );
};

class Stats extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      mapHistory: iList(),
    };

    this.loadMapHistory = this.loadMapHistory.bind(this);
  }

  loadMapHistory() {
    return get("get_map_history?pretty=1")
      .then((response) => showResponse(response, "get_map_history"))
      .then((data) => this.setState({ mapHistory: fromJS(data.result) }))
      .catch(handle_http_errors);
  }

  componentDidMount() {
    this.loadMapHistory();
  }
  render() {
    return <Grid container>
        <Grid item xs={12}>
            <MapList mapList={this.state.mapHistory} classes={this.props.classes} />
        </Grid>
    </Grid>;
  }
}

export default Stats;
