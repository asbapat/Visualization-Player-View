/**
 * Created by asb on 4/17/2017.
 */
function collapsibleTree() {

    d3.selectAll("svg").remove();
    d3.select("#tableContent").remove();
    d3.select('#playerDetail').remove();
    d3.select('#bpsChart').remove();
    document.getElementById("season_stats").style.display = "none";

    var margin = {top: 20, right: 20, bottom: 30, left: 200},
        width = 1200 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var xScale = d3.scale.linear().range([30, 550]).domain([0,38]);
    var xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    var yScale = d3.scale.linear().range([25, 200]);
    var yAxis = d3.svg.axis().scale(yScale).orient("left");

    var i = 0,
        duration = 750,
        root;

    var tree = d3.layout.tree()
        .size([height, width]);

    var diagonal = d3.svg.diagonal()
        .projection(function (d) {
            return [d.y, d.x];
        });

    var colorScale = d3.scale.ordinal()
        .domain(["Arsenal", "Aston Villa", "Blackburn Rovers", "Bolton Wanderers", "Chelsea", "Everton", "Fulham",
            "Liverpool", "Manchester City", "Manchester United", "Newcastle United", "Norwich City",
            "Queens Park Rangers", "Stoke City", "Sunderland", "Swansea City", "Tottenham Hotspur",
            "West Bromwich Albion", "Wigan Athletic", "Wolverhampton Wanderers"])
        .range(["#EF0107", "#7A003C", "#1B458F", "#2A3C7D", "#034694", "#274488", "#353233", "#D00027", "#5CBFEB",
            "#DA020E", "#231F20", "#00A150", "#005AA7", "#E03A3E", "#EB172B", "#000000", "#001C58", "#091453",
            "#005CAB", "#E67C2F"]);

    var svg = d3.select("#collapsibleTree").append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.json("./static/leaguejson/league.json", function (error, data) {
        if (error) throw error;

        root = data;
        root.x0 = height / 2;
        root.y0 = 0;

        root.children.forEach(collapse);
        update(root);
    });

    d3.select(self.frameElement).style("height", "800px");

    function collapse(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(collapse);
            d.children = null;
        }
    }
    function update(source) {

        var nodes = tree.nodes(root).reverse(),
            links = tree.links(nodes);

        // Normalize for fixed-depth.
        nodes.forEach(function (d) {
            d.y = d.depth * 120;
        });

        // Update the nodes…
        var node = svg.selectAll("g.node")
            .data(nodes, function (d) {
                return d.id || (d.id = ++i);
            });

        // Enter any new nodes at the parent's previous position.
        var nodeEnter = node.enter().append("g")
            .attr("class", "node")
            .attr("transform", function (d) {
                return "translate(" + source.y0 + "," + source.x0 + ")";
            })
            .on("click", click);

        nodeEnter.append("circle")
            .attr("r", 1e-6)
            .style("fill", function (d) {
                return d._children ? "lightsteelblue" : "#fff";
            });

        nodeEnter.append("text")
            .attr("x", function (d) {
                return d.children || d._children ? -10 : 10;
            })
            .attr("dy", ".35em")
            .attr("text-anchor", function (d) {
                return d.children || d._children ? "end" : "start";
            })
            .text(function (d) {
                return d.name;
            })
            .style("fill-opacity", 1e-6)
            .style("font-weight","bold")
            .style("font-size", "0.75em");

        nodeEnter.append("image")
            .attr("xlink:href", function(d){
                return d.image;
            })
            .attr("x", "-9px")
            .attr("y","-10px")
            .attr("width","20px")
            .attr("height", "20px");

        nodeEnter.append("image")
            .attr("xlink:href", function(d){
                return d.jersey_image;
            })
            .attr("x", "-7px")
            .attr("y","-8px")
            .attr("width","20px")
            .attr("height", "20px");

        // Transition nodes to their new position.
        var nodeUpdate = node.transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + d.y + "," + d.x + ")";
            });

        nodeUpdate.select("circle")
            .attr("r", 4.5)
            .style("fill", function (d) {
                return d._children ? "lightsteelblue" : "#fff";
            });

        nodeUpdate.select("text")
            .style("fill-opacity", 1);

        // Transition exiting nodes to the parent's new position.
        var nodeExit = node.exit().transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + source.y + "," + source.x + ")";
            })
            .remove();

        nodeExit.select("circle")
            .attr("r", 1e-6);

        nodeExit.select("text")
            .style("fill-opacity", 1e-6);

        // Update the links…
        var link = svg.selectAll("path.link")
            .data(links, function (d) {
                return d.target.id;
            });

        // Enter any new links at the parent's previous position.
        link.enter().insert("path", "g")
            .attr("class", "link")
            .attr("d", function (d) {
                var o = {x: source.x0, y: source.y0};
                return diagonal({source: o, target: o});
            });

        // Transition links to their new position.
        link.transition()
            .duration(duration)
            .attr("d", diagonal);

        // Transition exiting nodes to the parent's new position.
        link.exit().transition()
            .duration(duration)
            .attr("d", function (d) {
                var o = {x: source.x, y: source.y};
                return diagonal({source: o, target: o});
            })
            .remove();

        // Stash the old positions for transition.
        nodes.forEach(function (d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

// Toggle children on click.
    function click(d) {

        if(!d._children){
            d3.select("#tableContent").remove();
            d3.select('#playerDetail').remove();
            d3.select('#bpsChart').remove();
            var opt = document.getElementById("season_stats");
            var newData = opt.options[opt.selectedIndex].value;
            if(d[newData] != null) {
                makeLineChart(newData, d);

                d3.select('#season_stats')
                    .on('change', function () {
                        var newData = d3.event.target.value;
                        makeLineChart(newData, d);
                    });

                var playerTable = d3.select('#playerProfile')
                    .append('table')
                    .attr('id', 'tableContent')
                    .attr("width", "100%")
                    .attr("height", margin.top)
                    .attr("align", "center");

                var columns = [{src: d.player_image}];
                var logo = [{src: d.player_logo}];

                var headers = playerTable.append('thead').append('tr')
                    .selectAll('th')
                    .data(columns)
                    .enter()
                    .append('th')
                    .style("background", d.team_color);

                headers.append('img')
                    .attr('src', function (d) {
                        return d.src;
                    })
                    .attr('width', 100)
                    .attr('height', 100);
                //.style("float", "left");

                headers.append('text')
                    .data([d.name])
                    .attr("class", "textboxes")
                    .text(function (d) {
                        return d;
                    })
                    .attr("dx", 10)
                    .style("padding-left", "70px");

                headers.append('text')
                    .data([d.position])
                    .attr("class", "textboxes")
                    .text(function (d) {
                        return d;
                    })
                    .attr("dx", 10)
                    .style("padding-left", "25px");

                headers.append('img').data(logo)
                    .attr('src', function (d) {
                        return d.src;
                    })
                    .attr('width', 170)
                    .attr('height', 80)
                    .style("padding-left", "60px");
                //.style("float", "right");
                //.style("padding-left", "20px");

                var playerDetails = d3.select('#playerDetails')
                    .append('table')
                    .attr('id', 'playerDetail')
                    .attr("width", "75%")
                    .attr("height", height / 4)
                    .attr("align", "center");

                var heads = playerDetails.append('thead').append('tr')
                    .selectAll('th')
                    .data(["Time Played", "Goals", "Big Chances", "Total Fouls"])
                    .enter()
                    .append('th')
                    .text(function (d) {
                        return d;
                    })
                    .style("background", "lightyellow")
                    .style("height", "10px")
                    .style("text-align", "center");

                var body = playerDetails.append('tbody').append('tr')
                    .selectAll('td')
                    .data([d.time_played, d.goals, d.bigchances, d.totalFouls])
                    .enter()
                    .append('td')
                    .text(function (d) {
                        return d;
                    })
                    .style("height", "10px")
                    .style("text-align", "center");
            }

        }
        if (d.children) {
            d._children = d.children;
            d.children = null;
            d3.select("#teamlogo").remove();
            document.getElementById("season_stats").style.display = "none";
        } else {
            d.children = d._children;
            d._children = null;
            d3.select("#teamlogo").remove();
            //  document.getElementById("season_stats").style.display = "none";

            var teamDetails = svg.append("g")
                .append("svg:image")
                .attr("xlink:href", d.image)
                .attr("width",150)
                .attr("height",150)
                .attr("id", "teamlogo")
                .attr("x",850)
                .attr("y",0);
        }
        if (d.parent) {
            d.parent.children.forEach(function(element) {
                if (d !== element) {
                    collapse(element);
                }
            });
        }
        update(d);
    }

    function makeLineChart(selected_attribute, d) {
        document.getElementById("season_stats").style.display = "block";
        d3.select('#bpsChart').remove();

        var svg2 = d3.select("#lineChart").append("svg")
            .attr('id','bpsChart')
            .attr("class","svg2")
            .attr("width", 600)
            .attr("height", 220);
        var width = 600, height = 220;
        var weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38];

        if(parseInt(d3.max(d[selected_attribute])) == 0)
            yScale.domain([height - d3.max(d[selected_attribute]), d3.min(d[selected_attribute])]);
        else
            yScale.domain([d3.max(d[selected_attribute]), d3.min(d[selected_attribute])]);

        var line = d3.svg.line()
            .x(function(d,i){
                return xScale(weeks[i]);
            })
            .y(function (d, i) {
                return yScale(d);
            });

        svg2.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .append('text')
            .attr("class", "title")
            .text("Statistics Progression");

        svg2.append("g")
            .attr("class","x axis")
            .attr("transform","translate(0," + yScale(0) + ")")
            .call(xAxis)
            .append("text")
            .attr("class", "label")
            .attr("x", 590)
            .attr("y", 13)
            .style("text-anchor", "end")
            .text("Gameweek");

        svg2.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + xScale(0) + ",0)")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("x", -1)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .style("font-weight", "bold")
            //.style("font-size", "0.2em")
            .text("Metric");

        svg2.append("path")
            .attr("d", line(d[selected_attribute]))
            .attr("stroke", "#ff0000")
            .style("fill","none");
    }
}
