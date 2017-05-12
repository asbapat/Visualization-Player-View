/**
 * Created by Nipun on 10-05-2017.
 */

function bumpChart() {
    d3.selectAll("svg").remove();
    // d3.select("#canvas").remove();

    var margin = {top: 20, right: 180, bottom: 50, left: 30},
        width = 1200 - margin.left - margin.right,
        height = 520 - margin.top - margin.bottom;

    var speed = 400;

    var x = d3.scale.linear()
        .range([0,width]);

    var y = d3.scale.ordinal()
        .rangeRoundBands([height, 0], .1);

    var xAxis = d3.svg.axis()
        .scale(x)
        .tickSize(0)
        .orient("bottom");

    var xAxis1 = d3.svg.axis()
        .scale(x)
        .tickSize(0)
        .ticks(38)
        .orient("top");

    var yAxis = d3.svg.axis()
        .scale(y)
        .tickSize(-width)
        .tickPadding(10)
        .orient("left");

    var line = d3.svg.line()
        .x(function(d) { return x(d.matchday); })
        .y(function(d) { return y(d.position) + y.rangeBand()/2; });

    var svg = d3.select('#makeBumpChart').append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var clip = svg.append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", 0)
        .attr("height", height);

    d3.json("static/leaguejson/bump_chart.json", function(error, data) {
        if(error) throw error;

        y.domain(d3.range(1,d3.max(data.standing, function(club) { return d3.max(club.rank, function(d) { return d.position; }); }) + 1 ).reverse());
        xAxis.tickValues(data.standing[0].rank.map(function(d) { return d.matchday; }));
        x.domain(d3.extent(data.standing[0].rank.map(function(d) { return d.matchday; })));

        //set y axis
        svg.append("g")
            .attr("class", "y axis2")
            .call(yAxis);

        //set bottom axis position
        svg.append("g")
            .attr("class", "x axis2")
            .attr("transform", "translate(" + 0 + "," + 450  + ")")
            .call(xAxis);

        //set top axis
        svg.append("g")
            .attr("class", "x axis2")
            .call(xAxis1);

        var club = svg.selectAll(".club")
            .data(data.standing)
            .enter().append("g")
            .attr("class", "club");

        var path = club.append("path")
                .attr("class", "line")
                .style("stroke", function(d) { return d.color; })
                .style("stroke-width", 4)
                .style("fill","none")
                .attr("clip-path", function(d) { return "url(#clip)"; })
                .attr("d", function(d) { return line(d.rank); })
                .on("mouseover", function (d) {
                    club.style("opacity",0.2);
                    club.filter(function(path) {return path.teamName === d.teamName; }).style("opacity",1);
                })
                .on("mouseout", function (d) { club.style("opacity",1); })
            ;
        var circleStart = club.append("circle")
            .attr("cx", function(d) { return x(d.rank[0].matchday); })
            .attr("cy", function(d) { return y(d.rank[0].position) + y.rangeBand()/2; })
            .attr("r", 6)
            .style("stroke", function(d) { return d.color; })
            .style("stroke-width", 4)
            .style("fill", "white")
            .on("mouseover", function (d) {
                club.style("opacity",0.2);
                club.filter(function(path) {return path.teamName === d.teamName; }).style("opacity",1);
            })
            .on("mouseout", function (d) { club.style("opacity",1); });

        circleStart.append("image")
        // .attr("xlink:href", function(d){
        //     return d.image;
        // })
            .attr("xlink:href", "static/lib/images/logos/Sunderland.png")
            .attr("x", "9px")
            .attr("y","10px")
            .attr("width","25px")
            .attr("height", "25px");

        var circleEnd = club.append("circle")
            .attr("cx", function(d) { return x(d.rank[0].matchday); })
            .attr("cy", function(d) { return y(d.rank[0].position) + y.rangeBand()/2; })
            .attr("r", 6)
            .style("stroke", function(d) { return d.color; })
            .style("stroke-width", 4)
            .style("fill", "white")
            .on("mouseover", function (d) {
                club.style("opacity",0.2);
                club.filter(function(path) {return path.teamName === d.teamName; }).style("opacity",1);
            })
            .on("mouseout", function (d) { club.style("opacity",1); });

        circleEnd.append("image")
        // .attr("xlink:href", function(d){
        //     return d.image;
        // })
            .attr("xlink:href", "static/lib/images/logos/Sunderland.png")
            .attr("x", "9px")
            .attr("y","10px")
            .attr("width","25px")
            .attr("height", "25px");

        // text label for the x axis
        svg.append("text")
            .attr("x", width / 2 )
            .attr("y",  height + (margin.bottom/1.5))
            .attr("style","font-size:14px;") // to bold title
            .style("text-anchor", "middle")
            .text("Game in Season");

        var label = club.append("text")
            .attr("transform", function(d) { return "translate(" + x(d.rank[0].matchday) + "," + (y(d.rank[0].position) + y.rangeBand()/2) + ")"; })
            .attr("x", 8)
            .attr("dy", ".31em")
            .on("mouseover", function (d) {
                club.style("opacity",0.2);
                club.filter(function(path) {return path.teamName === d.teamName; }).style("opacity",1);
            })
            .on("mouseout", function (d) { club.style("opacity",1); })
            .style("cursor","pointer")
            .style("fill", function(d) { return d.color; })
            .style("font-weight", "bold")
            .text(function(d) { return ""+ d.rank[0].position + " " + d.teamName; });

        var matchday = 1;
        var transition = d3.transition()
            .duration(speed)
            .each("start", function start() {
                label.transition()
                    .duration(speed)
                    .ease('linear')
                    .attr("transform", function(d) { return "translate(" + x(d.rank[matchday].matchday) + "," + (y(d.rank[matchday].position) + y.rangeBand()/2) + ")"; })
                    .text(function(d) { return  " " +  " " + d.teamName; });

                circleEnd.transition()
                    .duration(speed)
                    .ease('linear')
                    .attr("cx", function(d) { return x(d.rank[matchday].matchday); })
                    .attr("cy", function(d) { return y(d.rank[matchday].position) + y.rangeBand()/2; });
                clip.transition()
                    .duration(speed)
                    .ease('linear')
                    .attr("width", x(matchday+1))
                    .attr("height", height);

                matchday+=1;
                if (matchday !== data.standing[0].rank.length) transition = transition.transition().each("start", start);

            });
    });
}
