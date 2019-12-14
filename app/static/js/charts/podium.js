

var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var colors = [
    '#FFB900',
    '#AAA9AD',
    '#847545',
    '#D3D3D3',
];

var Leaderboard = /** @class */ (function (_super) {
    __extends(Leaderboard, _super);
    function Leaderboard() {
        var _this = _super.call(this) || this;
        _this.state = {
            leaders: [],
            maxScore: 500
        };
        _this.getData = _this.getData.bind(_this);
        return _this;
    }
    Leaderboard.prototype.getData = function () {
        /* Here you can implement data fetching */
        session_id=document.getElementById('session_id').getAttribute('value');

        fetch('/getTopPoints?session_id='+session_id)
        .then(results =>{
          return results.json();
        }).then(output =>{
          leaders=[]
          for (i=0; i<output.length;i++){
            leaders.push({id: output[i][0], groupName: output[i][1], groupingName: output[i][2], score: output[i][3]})
          }

          var data = {
              success: true,
              leaders: leaders,
              maxScore: output[0][3]
          };

          this.setState({
              leaders: data.leaders,
              maxScore: data.maxScore
          });
        });


    };

    Leaderboard.prototype.componentWillMount = function () {
        this.getData();
        /*data is refreshing every 10 seconds*/
        setInterval(this.getData, 10000);
    };


    Leaderboard.prototype.render = function () {
        var _this = this;
        return (
            React.createElement("div", { className: "Leaderboard" },
            // React.createElement("h1", null, "Leaderboard"),
            React.createElement("div", { className: "leaders" }, this.state.leaders ? (this.state.leaders.map(function (el, i) { return (React.createElement("div", { key: el.id, style: {
                    animationDelay: i * 0.1 + 's'
                }, className: "leader" },
                React.createElement("div", { className: "leader-wrap" },
                    i < 3 ? (React.createElement("div", { style: {
                            backgroundColor: colors[i]
                        }, className: "leader-ava" },
                        React.createElement("svg", { fill: "#fff", xmlns: "http://www.w3.org/2000/svg", height: 24, width: 24, viewBox: "0 0 32 32" },
                            React.createElement("path", { d: "M 16 3 C 14.354991 3 13 4.3549901 13 6 C 13 7.125993 13.63434 8.112309 14.5625 8.625 L 11.625 14.5 L 7.03125 11.21875 C 7.6313215 10.668557 8 9.8696776 8 9 C 8 7.3549904 6.6450096 6 5 6 C 3.3549904 6 2 7.3549904 2 9 C 2 10.346851 2.9241199 11.470238 4.15625 11.84375 L 6 22 L 6 26 L 6 27 L 7 27 L 25 27 L 26 27 L 26 26 L 26 22 L 27.84375 11.84375 C 29.07588 11.470238 30 10.346852 30 9 C 30 7.3549901 28.645009 6 27 6 C 25.354991 6 24 7.3549901 24 9 C 24 9.8696781 24.368679 10.668557 24.96875 11.21875 L 20.375 14.5 L 17.4375 8.625 C 18.36566 8.112309 19 7.125993 19 6 C 19 4.3549901 17.645009 3 16 3 z M 16 5 C 16.564129 5 17 5.4358709 17 6 C 17 6.5641291 16.564129 7 16 7 C 15.435871 7 15 6.5641291 15 6 C 15 5.4358709 15.435871 5 16 5 z M 5 8 C 5.5641294 8 6 8.4358706 6 9 C 6 9.5641286 5.5641291 10 5 10 C 4.4358709 10 4 9.5641286 4 9 C 4 8.4358706 4.4358706 8 5 8 z M 27 8 C 27.564129 8 28 8.4358709 28 9 C 28 9.5641283 27.564128 10 27 10 C 26.435872 10 26 9.5641283 26 9 C 26 8.4358709 26.435871 8 27 8 z M 16 10.25 L 19.09375 16.4375 L 20.59375 16.8125 L 25.59375 13.25 L 24.1875 21 L 7.8125 21 L 6.40625 13.25 L 11.40625 16.8125 L 12.90625 16.4375 L 16 10.25 z M 8 23 L 24 23 L 24 25 L 8 25 L 8 23 z" })))) : null,
                    React.createElement("div", { className: "leader-content" },
                        React.createElement("div", { className: "leader-name" }, i +1+ '. ' + el.groupingName +' - '+ el.groupName),
                        React.createElement("div", { className: "leader-score" },

                            React.createElement("div", { className: "leader-score_title" }, el.score)))),
                React.createElement("div", { style: { animationDelay: 0.4 + i * 0.2 + 's' }, className: "leader-bar" },
                    i < 3 ? (
                    React.createElement("div", { style: {
                            backgroundColor: colors[i],
                            width: el.score / _this.state.maxScore * 100 + '%'
                        }, className: "bar" })):
                    (React.createElement("div", { style: {
                            backgroundColor: colors[3],
                            width: el.score / _this.state.maxScore * 100 + '%'
                        }, className: "bar" }))))); })) : (React.createElement("div", { className: "empty" }, "\u041F\u0443\u0441\u0442\u043E")))));
    };
    return Leaderboard;
}(React.Component));
ReactDOM.render(React.createElement(Leaderboard, null), document.getElementById('podium'));
